from models.review_request_model import ReviewModel
from models.property_request_model import PropertyRequestModel
from dynamo_client import DynamoClient
from models.property_response_model import PropertyResponseModel
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json
import utils
import operator


class RevletPropertyService:
    def __init__(self, client=None):
        self.DBClient = DynamoClient(client)

    def get_properties_by_postcode(self, postcode_hash):
        if not utils.validate_hash(postcode_hash):
            return utils.get_lambda_response(400, "Invalid Postcode")

        try:
            args = {
                "FilterExpression": Key("itemId").begins_with(postcode_hash)
                & Key("dataSelector").begins_with("META#")
            }
            response = self.DBClient.get_all_items(args)
        except Exception as e:
            return utils.get_lambda_response(400, str(e))

        if len(response) == 0:
            return utils.get_lambda_response(404, "No property found")

        return utils.get_lambda_response(200, json.dumps(response, default=str))

    def get_property_by_id(self, property_id):
        # Validate property ID
        if not utils.validate_property_id(property_id):
            return utils.get_lambda_response(400, "Invalid Property ID")

        try:
            query = Key("itemId").eq(property_id) & Key("dataSelector").begins_with(
                "META#"
            )
            response = self.DBClient.query_items(query)
        except Exception as e:
            return utils.get_lambda_response(400, str(e))

        if len(response) == 0:
            return utils.get_lambda_response(404, "No property found")

        return_property = PropertyResponseModel(**response[0])
        return utils.get_lambda_response(
            200, json.dumps(return_property.convert_to_dictionary(), default=str)
        )

    def post_property(self, body):
        new_property = PropertyRequestModel(**body)
        if not new_property.validate_property_postcode():
            return utils.get_lambda_response(400, "Invalid postcode")

        args = {"ConditionExpression": "attribute_not_exists(dataSelector)"}

        try:
            self.DBClient.post_item(
                new_property.convert_to_dictionary(),
                args,
            )
        except Exception as e:
            return utils.get_lambda_response(400, str(e))

        return utils.get_lambda_response(200, "{} Created".format(new_property.itemId))

    def update_property_details(self, property_id, body):
        args = {
            "ConditionExpression": "attribute_exists(itemId)",
        }

        if not utils.validate_property_id(property_id):
            return utils.get_lambda_response(400, "Invalid property ID")

        try:
            meta_key = utils.get_metadata_key_from_item_id(property_id)
            response = self.DBClient.update_item(
                property_id,
                meta_key,
                "set rooms=:r, parking=:p, garden=:g",
                {
                    ":r": int(body["rooms"]),
                    ":p": bool(body["parking"]),
                    ":g": bool(body["garden"]),
                },
                args,
            )
        except Exception as e:
            return utils.get_lambda_response(400, str(e))

        return_property = PropertyResponseModel(**response)
        return utils.get_lambda_response(
            200, json.dumps(return_property.convert_to_dictionary(), default=str)
        )

    def update_property_ratings(
        self, property_id, review: ReviewModel, update_function=operator.add
    ):
        review_property_response = self.get_property_by_id(property_id)
        if review_property_response["statusCode"] != 200:
            return review_property_response

        review_property_data = json.loads(review_property_response["body"])
        review_property = PropertyRequestModel(**review_property_data)

        try:
            review_property.update_property_ratings(review, update_function)

            put_property_args = {"ConditionExpression": "attribute_exists(itemId)"}
            response = self.DBClient.update_item(
                review_property.itemId,
                review_property.dataSelector,
                "set facilitiesRating=:fr, locationRating=:lr, managementRating=:mr, reviewCount=:rc, overallRating=:or",
                {
                    ":fr": int(review_property.facilitiesRating),
                    ":lr": int(review_property.locationRating),
                    ":mr": int(review_property.managementRating),
                    ":or": int(review_property.overallRating),
                    ":rc": int(review_property.reviewCount),
                },
                put_property_args,
            )
        except Exception as e:
            return utils.get_lambda_response(400, str(e))

        return_property = PropertyResponseModel(**response)
        return utils.get_lambda_response(
            200, json.dumps(return_property.convert_to_dictionary(), default=str)
        )

    def delete_property(self, property_id):
        args = {
            "ConditionExpression": "attribute_exists(itemId)",
        }

        if not utils.validate_property_id(property_id):
            return utils.get_lambda_response(400, "Invalid property ID")

        try:
            meta_key = utils.get_metadata_key_from_item_id(property_id)
            response = self.DBClient.delete_item(property_id, meta_key, args)

        except Exception as e:
            return utils.get_lambda_response(400, str(e))

        return utils.get_lambda_response(200, json.dumps(response, default=str))
