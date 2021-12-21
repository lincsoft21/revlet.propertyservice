import boto3
from botocore.exceptions import ClientError
import uuid
import json
import utils

PROPERTIES_TABLE = "revlet-properties"
DEFAULT_REGION = "eu-west-2"


class RevletPropertyService:
    def __init__(self, client=None, table=PROPERTIES_TABLE, region=DEFAULT_REGION):
        if not client:
            self.DYNAMO_CLIENT = boto3.resource("dynamodb", region_name=region)
            self.PROPERTYSERVICE_TABLE = self.DYNAMO_CLIENT.Table(table)
        else:
            self.DYNAMO_CLIENT = client
            self.PROPERTYSERVICE_TABLE = self.DYNAMO_CLIENT.Table(table)

    def get_properties(self, event, context):
        try:
            if not "id" in event["queryStringParameters"]:
                response = self.PROPERTYSERVICE_TABLE.scan()
            else:
                response = self.PROPERTYSERVICE_TABLE.get_item(
                    Key={"propertyId": event["queryStringParameters"]["id"]},
                )
        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        if "Item" in response:
            return utils.get_lambda_response(
                200, json.dumps(response["Item"], default=str)
            )
        elif "Items" in response:
            return utils.get_lambda_response(
                200, json.dumps(response["Items"], default=str)
            )

        return utils.get_lambda_response(404, "No property found")

    def post_property(self, event, context):
        data = json.loads(event["body"])

        # Use update_item if record already exists
        propertyId = str(uuid.uuid4())
        data.update({"propertyId": propertyId})

        self.PROPERTYSERVICE_TABLE.put_item(
            Item=data,
        )

        return utils.get_lambda_response(200, json.dumps({"propertyId": propertyId}))

    def update_property_details(self, event, context):
        data = json.loads(event["body"])

        if not event["queryStringParameters"]:
            return utils.get_lambda_response(400, "No property specified")
        else:
            if not "id" in event["queryStringParameters"]:
                return utils.get_lambda_response(400, "No property specified")

        try:
            response = self.PROPERTYSERVICE_TABLE.update_item(
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
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        return utils.get_lambda_response(
            200, json.dumps(response["Attributes"], default=str)
        )

    def delete_property(self, event, context):
        if not event["queryStringParameters"]:
            return utils.get_lambda_response(400, "No property specified")
        else:
            if not "id" in event["queryStringParameters"]:
                return utils.get_lambda_response(400, "No property specified")

        try:
            delete_response = self.PROPERTYSERVICE_TABLE.delete_item(
                Key={"propertyId": event["queryStringParameters"]["id"]},
                ReturnValues="ALL_OLD",
            )
        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        # Validate that a property has been deleted
        if not "Attributes" in delete_response:
            return utils.get_lambda_response(404, "Property does not exist")

        print(delete_response)
        return utils.get_lambda_response(
            200, "Property {} deleted".format(event["queryStringParameters"]["id"])
        )
