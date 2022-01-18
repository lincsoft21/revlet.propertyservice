from propertyservice_client import RevletPropertyService
import utils
import json

PROPERTYSERVICE_CLIENT = RevletPropertyService()


def get_properties(event, context):
    if "id" in event["queryStringParameters"]:
        id = event["queryStringParameters"]["id"]
        return PROPERTYSERVICE_CLIENT.get_properties(id)

    return PROPERTYSERVICE_CLIENT.get_properties()


def post_property(event, context):
    data = json.loads(event["body"])
    return PROPERTYSERVICE_CLIENT.post_property(data)


def update_property_details(event, context):
    data = json.loads(event["body"])

    if not event["queryStringParameters"]:
        return utils.get_lambda_response(400, "No property specified")
    else:
        if not "id" in event["queryStringParameters"]:
            return utils.get_lambda_response(400, "No property specified")

    return PROPERTYSERVICE_CLIENT.update_property_details(
        event["queryStringParameters"]["id"], data
    )


def delete_property(event, context):
    if not event["queryStringParameters"]:
        return utils.get_lambda_response(400, "No property specified")
    else:
        if not "id" in event["queryStringParameters"]:
            return utils.get_lambda_response(400, "No property specified")

    return PROPERTYSERVICE_CLIENT.delete_property(event["queryStringParameters"]["id"])
