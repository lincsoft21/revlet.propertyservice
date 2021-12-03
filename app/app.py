import boto3
import uuid
import json

DYNAMO_CLIENT = boto3.client("dynamodb", region_name="eu-west-2")


def get_properties(event, context):
    if "id" in event:
        response = DYNAMO_CLIENT.get_item(
            TableName="linsoft-revlet-properties",
            Key={"PropertyId": {"S": event["id"]}},
        )
    else:
        response = DYNAMO_CLIENT.scan(TableName="linsoft-revlet-properties")

    if "Item" in response:
        return get_lambda_response(200, json.dumps(response["Item"]))
    elif "Items" in response:
        return get_lambda_response(200, json.dumps(response["Items"]))

    return get_lambda_response(404, "No property found")


def post_property(event, context):
    # Use update_item if record already exists
    data = json.loads(event["body"])
    propertyId = str(uuid.uuid4())
    DYNAMO_CLIENT.put_item(
        TableName="linsoft-revlet-properties",
        Item={
            "PropertyId": {"S": propertyId},
            "Postcode": {"S": data["postcode"]},
            "StreetName": {"S": data["streetName"]},
        },
    )

    return get_lambda_response(200, json.dumps({"propertyId": propertyId}))


def get_lambda_response(status=200, data="", isBase64=False, headers={}):
    return {
        "isBase64Encoded": isBase64,
        "statusCode": status,
        "headers": headers,
        "body": data,
    }
