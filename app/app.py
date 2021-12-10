import boto3
import uuid
import json

DYNAMO_CLIENT = boto3.resource("dynamodb", region_name="eu-west-2")
PROPERTIES_TABLE = DYNAMO_CLIENT.Table("revlet-properties")


def get_properties(event, context):
    if "id" in event:
        response = PROPERTIES_TABLE.get_item(
            Key={"propertyId": event["id"]},
        )
    else:
        response = PROPERTIES_TABLE.scan()

    if "Item" in response:
        return get_lambda_response(200, json.dumps(response["Item"]))
    elif "Items" in response:
        return get_lambda_response(200, json.dumps(response["Items"]))

    return get_lambda_response(404, "No property found")


def post_property(event, context):
    # Use update_item if record already exists
    data = json.loads(event["body"])
    propertyId = str(uuid.uuid4())

    data.update({"propertyId": propertyId})
    print(data)

    PROPERTIES_TABLE.put_item(
        Item=data,
    )

    return get_lambda_response(200, json.dumps({"propertyId": propertyId}))


def get_lambda_response(status=200, data="", isBase64=False, headers={}):
    return {
        "isBase64Encoded": isBase64,
        "statusCode": status,
        "headers": headers,
        "body": data,
    }
