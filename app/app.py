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

_propertyhandler = RevletPropertyService(_dbclient, _responder)
_reviewhandler = RevletReviewService(_dbclient, _responder)


def get_properties(event, context):
    if utils.validate_query_params("p", event):
        return _propertyhandler.get_properties_by_postcode(
            event["queryStringParameters"]["p"]
        )
    elif utils.validate_query_params("id", event):
        return _propertyhandler.get_property_by_id(event["queryStringParameters"]["id"])

    return _responder.return_invalid_request_response("Missing property details")


def get_property_by_id(event, context):
    return _propertyhandler.get_property_by_id(event["pathParameters"]["id"])


def post_property(event, context):
    data = json.loads(event["body"])
    return _propertyhandler.post_property(data)


def update_property_details(event, context):
    data = json.loads(event["body"])

    if not utils.validate_query_params("id", event):
        return _responder.return_invalid_request_response("Request missing property ID")

    return _propertyhandler.update_property_details(
        event["queryStringParameters"]["id"], data
    )


def delete_property(event, context):
    if not utils.validate_query_params("id", event):
        return _responder.return_invalid_request_response("Request missing property ID")

    return _propertyhandler.delete_property(event["queryStringParameters"]["id"])


def get_reviews(event, context):
    # Given a valid property details, get all reviews associated
    if not utils.validate_query_params("id", event):
        return _responder.return_invalid_request_response("Request missing property ID")

    return _reviewhandler.get_reviews(event["queryStringParameters"]["id"])


def post_review(event, context):
    if not utils.validate_query_params("id", event):
        return _responder.return_invalid_request_response("Request missing property ID")

    data = json.loads(event["body"])
    return _reviewhandler.post_review(event["queryStringParameters"]["id"], data)


def delete_review(event, context):
    if not utils.validate_query_params("id", event) or not utils.validate_query_params(
        "r", event
    ):
        return _responder.return_invalid_request_response(
            "Request missing property details"
        )

    return _reviewhandler.delete_review(
        event["queryStringParameters"]["id"], event["queryStringParameters"]["r"]
    )
