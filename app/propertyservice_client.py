import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import uuid
import json
import utils

PROPERTIES_TABLE = "revlet-dev-properties"
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
        id_defined = False
        try:
            if (
                not event["queryStringParameters"]
                or not "id" in event["queryStringParameters"]
            ):
                response = self.PROPERTYSERVICE_TABLE.scan(
                    FilterExpression=Attr("dataSelector").begins_with("METADATA#")
                )
            else:
                id_defined = True
                response = self.PROPERTYSERVICE_TABLE.query(
                    KeyConditionExpression=Key("propertyId").eq(
                        event["queryStringParameters"]["id"]
                    )
                )
        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        if not "Items" in response:
            return utils.get_lambda_response(
                400, "An error occurred fetching property data"
            )

        if len(response["Items"]) == 0 and id_defined:
            return utils.get_lambda_response(404, "No property found")

        return utils.get_lambda_response(
            200, json.dumps(response["Items"], default=str)
        )

    def post_property(self, event, context):
        data = json.loads(event["body"])

        # Create ID for property
        propertyId = str(uuid.uuid4())
        data.update(
            {"propertyId": propertyId, "dataSelector": "METADATA#{}".format(propertyId)}
        )

        self.PROPERTYSERVICE_TABLE.put_item(
            Item=data,
        )

        return utils.get_lambda_response(200, json.dumps({"propertyId": propertyId}))

    def update_property_details(self, id, body):
        try:
            response = self.PROPERTYSERVICE_TABLE.update_item(
                Key={
                    "propertyId": id,
                    "dataSelector": "METADATA#{}".format(id),
                },
                ConditionExpression="attribute_exists(propertyId)",
                UpdateExpression="set rooms=:r, parking=:p, garden=:g",
                ExpressionAttributeValues={
                    ":r": int(body["rooms"]),
                    ":p": bool(body["parking"]),
                    ":g": bool(body["garden"]),
                },
                ReturnValues="UPDATED_NEW",
            )
        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        return utils.get_lambda_response(
            200, json.dumps(response["Attributes"], default=str)
        )

    def delete_property(self, id):
        # Delete all items under property (reviews and metadata)
        delete_items = self.PROPERTYSERVICE_TABLE.query(
            KeyConditionExpression=Key("propertyId").eq(id)
        )

        if len(delete_items["Items"]) == 0:
            return utils.get_lambda_response(404, "Property does not exist")

        for item in delete_items["Items"]:
            try:
                self.PROPERTYSERVICE_TABLE.delete_item(
                    Key={
                        "propertyId": item["propertyId"],
                        "dataSelector": item["dataSelector"],
                    },
                )

            except ClientError as e:
                return utils.get_lambda_response(400, e.response["Error"]["Message"])

        return utils.get_lambda_response(200, "Property {} deleted".format(id))
