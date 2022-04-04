from models.property import Property, PropertyModel
from models.review import ReviewRequestModel, Review, ReviewModel
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
        try:
            query = Key("itemID").eq(property_id) & Key("dataSelector").begins_with(
                "REV-"
            )
            response = self._dbclient.query_items(query)
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return self._responder.return_success_response(response)

    def post_review(self, review: ReviewRequestModel):
        try:
            new_review = Review(review)
            if not new_review.validate_item():
                return self._responder.return_invalid_request_response("Invalid review")

            review_property_response = self._propertyclient.get_property_by_id(
                review.itemID
            )
            if review_property_response["statusCode"] != 200:
                return review_property_response

            post_review_args = {
                "ConditionExpression": "attribute_not_exists(dataSelector)"
            }
            print(new_review.review)
            # Create new review in database before updating property
            self._dbclient.post_item(new_review.response_object(), post_review_args)

            # Parse to PropertyModel and update property ratings
            review_property = PropertyModel(
                **json.loads(review_property_response["body"])
            )
            new_review.update_property_ratings(review_property)
            property_update_response = self._propertyclient.update_property_ratings(
                review_property
            )
            if property_update_response["statusCode"] != 200:
                return property_update_response

        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return self._responder.return_success_response(
            "{} Created".format(new_review.review.dataSelector)
        )

    def delete_review(self, property_id, review_key):
        args = {
            "ConditionExpression": "attribute_exists(itemID) and attribute_exists(dataSelector)"
        }
        try:
            review_property_response = self._propertyclient.get_property_by_id(
                property_id
            )
            if review_property_response["statusCode"] != 200:
                return review_property_response

            delete_response = self._dbclient.delete_item(property_id, review_key, args)

            # Update property to remove ratings
            delete_review = Review(delete_response)
            delete_review_property = PropertyModel(
                **json.loads(review_property_response["body"])
            )
            updated_review_property = delete_review.update_property_ratings(
                delete_review_property, operator.sub
            )

            response = self._propertyclient.update_property_ratings(
                updated_review_property
            )
            if response["statusCode"] != 200:
                return response
        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return_deleted_review = ReviewModel(**delete_response)
        return self._responder.return_success_response(asdict(return_deleted_review))
