import boto3
from botocore.exceptions import ClientError
import uuid
import json

DYNAMO_CLIENT = boto3.resource("dynamodb", region_name="eu-west-2")
PROPERTIES_TABLE = DYNAMO_CLIENT.Table("revlet-properties")


def get_properties(event, context):
    try:
        if event["queryStringParameters"]:
            if "id" in event["queryStringParameters"]:
                response = PROPERTIES_TABLE.get_item(
                    Key={"propertyId": event["queryStringParameters"]["id"]},
                )
        else:
            response = PROPERTIES_TABLE.scan()
    except ClientError as e:
        return get_lambda_response(400, e.response["Error"]["Message"])

    if "Item" in response:
        return get_lambda_response(200, json.dumps(response["Item"], default=str))
    elif "Items" in response:
        return get_lambda_response(200, json.dumps(response["Items"], default=str))

    return get_lambda_response(404, "No property found")


def post_property(event, context):
    data = json.loads(event["body"])

    # Use update_item if record already exists
    propertyId = str(uuid.uuid4())
    data.update({"propertyId": propertyId})

    PROPERTIES_TABLE.put_item(
        Item=data,
    )

    return get_lambda_response(200, json.dumps({"propertyId": propertyId}))


def update_property_details(event, context):
    data = json.loads(event["body"])

    if not event["queryStringParameters"]:
        return get_lambda_response(400, "No property specified")
    else:
        if not "id" in event["queryStringParameters"]:
            return get_lambda_response(400, "No property specified")

    try:
        response = PROPERTIES_TABLE.update_item(
            Key={"propertyId": event["queryStringParameters"]["id"]},
            UpdateExpression="set details.rooms=:r, details.parking=:p, details.garden=:g",
            ExpressionAttributeValues={
                ":r": int(data["rooms"]),
                ":p": bool(data["parking"]),
                ":g": bool(data["garden"]),
            },
            ReturnValues="UPDATED_NEW",
        )
    except ClientError as e:
        return get_lambda_response(400, e.response["Error"]["Message"])

    return get_lambda_response(200, json.dumps(response["Attributes"], default=str))


def delete_property(event, context):
    if not event["queryStringParameters"]:
        return get_lambda_response(400, "No property specified")
    else:
        if not "id" in event["queryStringParameters"]:
            return get_lambda_response(400, "No property specified")

    try:
        PROPERTIES_TABLE.delete_item(
            Key={"propertyId": event["queryStringParameters"]["id"]}
        )
    except ClientError as e:
        return get_lambda_response(400, e.response["Error"]["Message"])

    return get_lambda_response(
        200, "Property {} deleted".format(event["queryStringParameters"]["id"])
    )


def get_lambda_response(status=200, data="", headers={}, isBase64=False):
    return {
        "isBase64Encoded": isBase64,
        "statusCode": status,
        "headers": headers,
        "body": data,
    }
