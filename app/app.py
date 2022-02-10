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

    return _responder.return_invalid_request_response("Missing postcode in request")


def get_property_by_id(event, context):
    return _propertyhandler.get_property_by_id(event["pathParameters"]["id"])


def post_property(event, context):
    data = json.loads(event["body"])
    return _propertyhandler.post_property(data)


def update_property_details(event, context):
    data = json.loads(event["body"])

    return _propertyhandler.update_property_details(event["pathParameters"]["id"], data)


def delete_property(event, context):
    return _propertyhandler.delete_property(event["pathParameters"]["id"])


def get_reviews(event, context):
    return _reviewhandler.get_reviews(event["pathParameters"]["id"])


def post_review(event, context):
    data = json.loads(event["body"])
    return _reviewhandler.post_review(event["pathParameters"]["id"], data)


def delete_review(event, context):
    return _reviewhandler.delete_review(
        event["pathParameters"]["id"], event["pathParameters"]["reviewId"]
    )
