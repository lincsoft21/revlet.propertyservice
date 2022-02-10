from models.property import Property, PropertyModel
from responders.lambda_responder import LambdaResponder
from models.review import ReviewModel
from data.dynamo_client import DynamoClient
from boto3.dynamodb.conditions import Key, Attr
from dataclasses import asdict
import json
import utils
import operator


class RevletPropertyService:
    def __init__(self, db_client: DynamoClient, responder: LambdaResponder):
        self._dbclient = db_client
        self._responder = responder

    def get_properties_by_postcode(self, postcode_hash):
        if not utils.validate_hash(postcode_hash):
            return self._responder.return_invalid_request_response("Invalid postcode")

        try:
            args = {
                "FilterExpression": Key("itemID").begins_with(postcode_hash)
                & Key("dataSelector").begins_with("META#")
            }
            response = self._dbclient.get_all_items(args)
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return self._responder.return_success_response(response)

    def get_property_by_id(self, property_id):
        # Validate property ID
        if not utils.validate_property_id(property_id):
            return self._responder.return_invalid_request_response(
                "Invalid property ID"
            )

        try:
            query = Key("itemID").eq(property_id) & Key("dataSelector").begins_with(
                "META#"
            )
            response = self._dbclient.query_items(query)
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        if len(response) == 0:
            return self._responder.return_not_found_response("Property not found")

        return_property = PropertyModel(**response[0])
        return self._responder.return_success_response(asdict(return_property))

    def post_property(self, body):
        new_property = Property(**body)
        if not new_property.validate_item():
            return self._responder.return_invalid_request_response("Invalid property")

        args = {"ConditionExpression": "attribute_not_exists(dataSelector)"}

        try:
            self._dbclient.post_item(
                new_property.response_object(),
                args,
            )
        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return self._responder.return_success_response(
            "{} Created".format(new_property.property.itemID)
        )

    def update_property_details(self, property_id, body):
        args = {
            "ConditionExpression": "attribute_exists(itemID)",
        }

        if not utils.validate_property_id(property_id):
            return self._responder.return_invalid_request_response(
                "Invalid property ID"
            )

        try:
            meta_key = utils.get_metadata_key_from_item_id(property_id)
            response = self._dbclient.update_item(
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
        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return_property = PropertyModel(**response)
        return self._responder.return_success_response(asdict(return_property))

    def update_property_ratings(
        self, property_id, review: ReviewModel, update_function=operator.add
    ):
        review_property_response = self.get_property_by_id(property_id)
        if review_property_response["statusCode"] != 200:
            return review_property_response

        review_property_data = json.loads(review_property_response["body"])
        review_property = Property(**review_property_data)

        try:
            review_property.update_property_ratings(review, update_function)

            put_property_args = {"ConditionExpression": "attribute_exists(itemID)"}
            response = self._dbclient.update_item(
                review_property.property.itemID,
                review_property.property.dataSelector,
                "set facilitiesRating=:fr, locationRating=:lr, managementRating=:mr, reviewCount=:rc, overallRating=:or",
                {
                    ":fr": int(review_property.property.facilitiesRating),
                    ":lr": int(review_property.property.locationRating),
                    ":mr": int(review_property.property.managementRating),
                    ":or": int(review_property.property.overallRating),
                    ":rc": int(review_property.property.reviewCount),
                },
                put_property_args,
            )
        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return_property = PropertyModel(**response)
        return self._responder.return_success_response(asdict(return_property))

    def delete_property(self, property_id):
        args = {
            "ConditionExpression": "attribute_exists(itemID)",
        }

        if not utils.validate_property_id(property_id):
            return self._responder.return_invalid_request_response(
                "Invalid property ID"
            )

        try:
            meta_key = utils.get_metadata_key_from_item_id(property_id)
            response = self._dbclient.delete_item(property_id, meta_key, args)

        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return_deleted_property = PropertyModel(**response)
        return self._responder.return_success_response(asdict(return_deleted_property))
