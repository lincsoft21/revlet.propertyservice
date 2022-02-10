from models.review import Review, ReviewModel
from responders.lambda_responder import LambdaResponder
from handlers.property_client import RevletPropertyService
from data.dynamo_client import DynamoClient
import utils
import json
from boto3.dynamodb.conditions import Key
import operator
from dataclasses import asdict


class RevletReviewService:
    def __init__(self, db_client: DynamoClient, responder: LambdaResponder):
        self._dbclient = db_client
        self._propertyclient = RevletPropertyService(db_client, responder)
        self._responder = responder

    def get_reviews(self, property_id):
        if not utils.validate_property_id(property_id):
            return self._responder.return_invalid_request_response(
                "Invalid property ID"
            )

        try:
            query = Key("itemID").eq(property_id) & Key("dataSelector").begins_with(
                "REV#"
            )
            response = self._dbclient.query_items(query)
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return self._responder.return_success_response(response)

    def post_review(self, property_id, body):
        if not utils.validate_property_id(property_id):
            return self._responder.return_invalid_request_response(
                "Invalid property ID"
            )

        try:
            new_review = Review(property_id, **body)
            if not new_review.validate_item():
                return self._responder.return_invalid_request_response("Invalid review")

            response = self._propertyclient.update_property_ratings(
                property_id, new_review.review
            )
            if response["statusCode"] != 200:
                return response

            post_review_args = {
                "ConditionExpression": "attribute_not_exists(dataSelector)"
            }

            # Create new review in database
            self._dbclient.post_item(new_review.response_object(), post_review_args)

        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return self._responder.return_success_response(
            "{} Created".format(new_review.review.dataSelector)
        )

    def delete_review(self, property_id, review_key):
        if not utils.validate_review_key(review_key):
            return self._responder.return_invalid_request_response("Invalid review key")

        args = {"ConditionExpression": "attribute_exists(dataSelector)"}
        try:
            delete_response = self._dbclient.delete_item(property_id, review_key, args)

            # Update property to remove ratings
            delete_review = ReviewModel(**delete_response)
            response = self._propertyclient.update_property_ratings(
                property_id, delete_review, operator.sub
            )
            if response["statusCode"] != 200:
                raise Exception("Failed to update property ratings")
        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return_deleted_review = ReviewModel(**delete_response)
        return self._responder.return_success_response(asdict(return_deleted_review))
