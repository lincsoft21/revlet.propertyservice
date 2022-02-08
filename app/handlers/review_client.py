from models.property_response_model import PropertyResponseModel
from handlers.property_client import RevletPropertyService
from models.review_request_model import ReviewModel
from data.dynamo_client import DynamoClient
from models.property_request_model import PropertyRequestModel
import utils
import json
from boto3.dynamodb.conditions import Key, Attr
import operator


class RevletReviewService:
    def __init__(self, db_client: DynamoClient):
        self.DBClient = db_client
        self.PropertyClient = RevletPropertyService(db_client)

    def get_reviews(self, property_id):
        if not utils.validate_property_id(property_id):
            return utils.get_lambda_response(400, "Invalid property ID")

        try:
            query = Key("itemId").eq(property_id) & Key("dataSelector").begins_with(
                "REV#"
            )
            response = self.DBClient.query_items(query)
        except Exception as e:
            return utils.get_lambda_response(500, str(e))

        return utils.get_lambda_response(200, json.dumps(response, default=str))

    def post_review(self, property_id, body):
        if not utils.validate_property_id(property_id):
            return utils.get_lambda_response(400, "Invalid property ID")

        try:
            new_review = ReviewModel(property_id, **body)
            if not new_review.validate_review_tenancy_dates():
                return utils.get_lambda_response(400, "Invalid tenancy dates")

            response = self.PropertyClient.update_property_ratings(
                property_id, new_review
            )
            if response["statusCode"] != 200:
                return response

            post_review_args = {
                "ConditionExpression": "attribute_not_exists(data_selector)"
            }

            # Create new review in database
            self.DBClient.post_item(
                new_review.convert_to_dictionary(), post_review_args
            )

        except Exception as e:
            return utils.get_lambda_response(500, str(e))

        return utils.get_lambda_response(200, "{} Created".format(new_review.itemId))

    def delete_review(self, property_id, review_hash):
        review_key = "REV#{}".format(review_hash)
        # args = {"ConditionExpression": "attribute_exists(data_selector)"}
        try:
            delete_response = self.DBClient.delete_item(property_id, review_key)

            # Update property to remove ratings
            delete_review = ReviewModel(**delete_response)
            response = self.PropertyClient.update_property_ratings(
                property_id, delete_review, operator.sub
            )
            if response["statusCode"] != 200:
                return response
        except Exception as e:
            return utils.get_lambda_response(400, str(e))

        return utils.get_lambda_response(200, json.dumps(delete_response, default=str))
