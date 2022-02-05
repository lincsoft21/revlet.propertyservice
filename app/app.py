from review_client import RevletReviewService
from propertyservice_client import RevletPropertyService
import utils
import json

PROPERTYSERVICE_CLIENT = RevletPropertyService()
REVIEWSERVICE_CLIENT = RevletReviewService()


def get_properties(event, context):
    if not utils.validate_query_params(["p"], event):
        return utils.get_lambda_response(400, "Request missing property details")

    postcode = event["queryStringParameters"]["p"]
    if not utils.validate_query_params(["s"], event):
        return PROPERTYSERVICE_CLIENT.get_properties_by_postcode(postcode)

    street_name = event["queryStringParameters"]["s"]
    return PROPERTYSERVICE_CLIENT.get_property_by_postcode_and_streetname(
        postcode, street_name
    )


def post_property(event, context):
    data = json.loads(event["body"])
    return PROPERTYSERVICE_CLIENT.post_property(data)


def update_property_details(event, context):
    data = json.loads(event["body"])

    if not utils.validate_query_params(["p", "s"], event):
        return utils.get_lambda_response(400, "Request missing property details")

    return PROPERTYSERVICE_CLIENT.update_property_details(
        event["queryStringParameters"]["p"], event["queryStringParameters"]["s"], data
    )


def delete_property(event, context):
    if not utils.validate_query_params(["p", "s"], event):
        return utils.get_lambda_response(400, "Request missing property details")

    return PROPERTYSERVICE_CLIENT.delete_property(
        event["queryStringParameters"]["p"], event["queryStringParameters"]["s"]
    )


def get_reviews(event, context):
    # Given a valid property details, get all reviews associated
    if not utils.validate_query_params(["p", "s"], event):
        return utils.get_lambda_response(400, "Request missing property details")

    return REVIEWSERVICE_CLIENT.get_reviews(
        event["queryStringParameters"]["p"], event["queryStringParameters"]["s"]
    )


def post_review(event, context):
    if not utils.validate_query_params(["p", "s"], event):
        return utils.get_lambda_response(400, "Request missing property details")

    data = json.loads(event["body"])
    return REVIEWSERVICE_CLIENT.post_item(data)


def delete_review(event, context):
    if not utils.validate_query_params(["id"], event):
        return utils.get_lambda_response(400, "Request missing property details")

    return REVIEWSERVICE_CLIENT.delete_review(event["queryStringParameters"]["id"])
