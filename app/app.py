from propertyservice_client import RevletPropertyService
import utils
import json

PROPERTYSERVICE_CLIENT = RevletPropertyService()


def get_properties(event, context):
    if event["queryStringParameters"]:
        if "p" in event["queryStringParameters"]:
            postcode = event["queryStringParameters"]["p"]
            return PROPERTYSERVICE_CLIENT.get_properties(postcode)

    return PROPERTYSERVICE_CLIENT.get_properties()


def post_property(event, context):
    data = json.loads(event["body"])
    return PROPERTYSERVICE_CLIENT.post_property(data)


def update_property_details(event, context):
    data = json.loads(event["body"])

    if not event["queryStringParameters"]:
        return utils.get_lambda_response(400, "Invalid request")
    else:
        if (
            not "p" in event["queryStringParameters"]
            or "s" in event["queryStringParameters"]
        ):
            return utils.get_lambda_response(400, "Request missing property details")

    return PROPERTYSERVICE_CLIENT.update_property_details(
        event["queryStringParameters"]["p"], event["queryStringParameters"]["s"], data
    )


def delete_property(event, context):
    if not event["queryStringParameters"]:
        return utils.get_lambda_response(400, "No property specified")
    else:
        if (
            not "p" in event["queryStringParameters"]
            or "s" in event["queryStringParameters"]
        ):
            return utils.get_lambda_response(400, "Request missing property details")

    return PROPERTYSERVICE_CLIENT.delete_property(
        event["queryStringParameters"]["p"], event["queryStringParameters"]["s"]
    )
