from middleware.request_validation import RequestValidator
from responders.lambda_responder import LambdaResponder
from data.dynamo_client import DynamoClient
from handlers.review_client import RevletReviewService
from handlers.property_client import RevletPropertyService
import utils
import json
import os

PROPERTIES_TABLE = "revlet-propertyservice-{}-db".format(
    os.environ.get("REVLET_ENV", "dev")
)

_responder = LambdaResponder()
_dbclient = DynamoClient(PROPERTIES_TABLE)

_requestValidator = RequestValidator()

_propertyhandler = RevletPropertyService(_dbclient, _responder)
_reviewhandler = RevletReviewService(_dbclient, _responder)


def get_properties(event, context):
    if _requestValidator.validate_query_params("p", event):
        p_hash = utils.get_key_hash(event["queryStringParameters"]["p"])
        return _propertyhandler.get_properties_by_postcode(p_hash)

    return _responder.return_invalid_request_response("Missing postcode in request")


def get_property_by_id(event, context):
    if not _requestValidator.validate_property_id(event["pathParameters"]["id"]):
        return _responder.return_invalid_request_response("Invalid property ID")

    return _propertyhandler.get_property_by_id(event["pathParameters"]["id"])


def post_property(event, context):
    data = json.loads(event["body"])

    # Get authenticated user ID
    user = event["requestContext"]["authorizer"]["claims"]["sub"]
    new_property = _requestValidator.validate_property_request(data, user)
    if not new_property:
        return _responder.return_invalid_request_response("Invalid property model")

    return _propertyhandler.post_property(new_property)


def update_property_details(event, context):
    data = json.loads(event["body"])

    # Validate user, property ID
    if not _requestValidator.validate_property_id(event["pathParameters"]["id"]):
        return _responder.return_invalid_request_response("Invalid property ID")

    # Get authenticated user ID
    user = event["requestContext"]["authorizer"]["claims"]["sub"]

    updated_property = _requestValidator.validate_property_update_request(
        event["pathParameters"]["id"], data, user
    )
    if not updated_property:
        return _responder.return_invalid_request_response("Invalid property request")

    return _propertyhandler.update_property_details(updated_property)


def delete_property(event, context):
    if not _requestValidator.validate_property_id(event["pathParameters"]["id"]):
        return _responder.return_invalid_request_response("Invalid property ID")

    return _propertyhandler.delete_property(event["pathParameters"]["id"])


def get_reviews(event, context):
    if not _requestValidator.validate_property_id(event["pathParameters"]["id"]):
        return _responder.return_invalid_request_response("Invalid property ID")

    return _reviewhandler.get_reviews(event["pathParameters"]["id"])


def post_review(event, context):
    if not _requestValidator.validate_property_id(event["pathParameters"]["id"]):
        return _responder.return_invalid_request_response("Invalid property ID")

    # Get authenticated user ID
    user = event["requestContext"]["authorizer"]["claims"]["sub"]

    data = json.loads(event["body"])
    data["itemID"] = event["pathParameters"]["id"]
    new_review = _requestValidator.validate_review_request(data, user)
    if not new_review:
        return _responder.return_invalid_request_response("Invalid review model")

    return _reviewhandler.post_review(new_review)


def delete_review(event, context):
    if not _requestValidator.validate_property_id(
        event["pathParameters"]["id"]
    ) or not _requestValidator.validate_review_key(event["pathParameters"]["reviewId"]):
        return _responder.return_invalid_request_response("Invalid property ID")

    return _reviewhandler.delete_review(
        event["pathParameters"]["id"], event["pathParameters"]["reviewId"]
    )
