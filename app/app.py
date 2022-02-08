from review_client import RevletReviewService
from property_client import RevletPropertyService
import utils
import json

PROPERTYSERVICE_CLIENT = RevletPropertyService()
REVIEWSERVICE_CLIENT = RevletReviewService()


def get_properties(event, context):
    if event["queryStringParameters"]["p"]:
        return PROPERTYSERVICE_CLIENT.get_properties_by_postcode(
            event["queryStringParameters"]["p"]
        )
    elif event["queryStringParameters"]["id"]:
        return PROPERTYSERVICE_CLIENT.get_property_by_id(
            event["queryStringParameters"]["id"]
        )

    return utils.get_lambda_response(400, "Request missing property details")


def post_property(event, context):
    data = json.loads(event["body"])
    return PROPERTYSERVICE_CLIENT.post_property(data)


def update_property_details(event, context):
    data = json.loads(event["body"])

    if not utils.validate_query_params(["id"], event):
        return utils.get_lambda_response(400, "Request missing property ID")

    return PROPERTYSERVICE_CLIENT.update_property_details(
        event["queryStringParameters"]["id"], data
    )


def delete_property(event, context):
    if not utils.validate_query_params(["id"], event):
        return utils.get_lambda_response(400, "Request missing property ID")

    return PROPERTYSERVICE_CLIENT.delete_property(event["queryStringParameters"]["id"])


def get_reviews(event, context):
    # Given a valid property details, get all reviews associated
    if not utils.validate_query_params(["id"], event):
        return utils.get_lambda_response(400, "Request missing property ID")

    return REVIEWSERVICE_CLIENT.get_reviews(event["queryStringParameters"]["id"])


def post_review(event, context):
    if not utils.validate_query_params(["id"], event):
        return utils.get_lambda_response(400, "Request missing property ID")

    data = json.loads(event["body"])
    return REVIEWSERVICE_CLIENT.post_item(event["querryStringParams"]["id"], data)


def delete_review(event, context):
    if not utils.validate_query_params(["id", "r"], event):
        return utils.get_lambda_response(400, "Request missing property or review details")

    return REVIEWSERVICE_CLIENT.delete_review(event["queryStringParameters"]["id"], event["queryStringParams"]["r"])
