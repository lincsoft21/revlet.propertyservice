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

    def get_properties(self, postcode=None):
        filter_defined = False
        try:
            if postcode:
                filter_defined = True
                postcode_filter = utils.generate_property_key(postcode)
                response = self.PROPERTYSERVICE_TABLE.query(
                    KeyConditionExpression=Key("propertyId").eq(postcode_filter)
                )
            
            else:
                response = self.PROPERTYSERVICE_TABLE.scan(
                    FilterExpression=Attr("dataSelector").begins_with("METADATA#")
                )
        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        if len(response["Items"]) == 0 and filter_defined:
            return utils.get_lambda_response(404, "No property found")

        return utils.get_lambda_response(
            200, json.dumps(response["Items"], default=str)
        )

    def post_property(self, body):
        # Create ID for property
        property_id = utils.generate_property_key(body["postcode"])
        data_selector = utils.generate_property_key(body["streetName"], "selector")
        index_pk = "{}#{}".format(property_id, data_selector)

        # Merge with index fields
        body.update(
            {
                "propertyId": property_id,
                "dataSelector": data_selector,
                "reviewIndexPK": index_pk,
                "reviewIndexSK": data_selector,
            }
        )

        try:
            self.PROPERTYSERVICE_TABLE.put_item(
                Item=body,
                ConditionExpression="attribute_not_exists(dataSelector)",
            )
        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        return utils.get_lambda_response(200, "{} Created".format(property_id))

    def update_property_details(self, postcode, street_name, body):
        property_id = utils.generate_property_key(postcode)
        data_selector = utils.generate_property_key(street_name, type="selector")

        try:
            response = self.PROPERTYSERVICE_TABLE.update_item(
                Key={
                    "propertyId": property_id,
                    "dataSelector": data_selector,
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

    def delete_property(self, postcode, street_name):
        property_id = utils.generate_property_key(postcode)
        data_selector = utils.generate_property_key(street_name, "selector")

        try:
            response = self.PROPERTYSERVICE_TABLE.delete_item(
                Key={
                    "propertyId": property_id,
                    "dataSelector": data_selector,
                },
                ConditionExpression="attribute_exists(propertyId)",
                ReturnValues="ALL_OLD",
            )

        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        return utils.get_lambda_response(200, json.dumps(response["Attributes"], default=str))
