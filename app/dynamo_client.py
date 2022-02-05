from models.db_item import PropertyServiceItem
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

PROPERTIES_TABLE = "revlet-propertyservice-{}-db".format(
    os.environ.get("REVLET_ENV", "test")
)
DEFAULT_REGION = "eu-west-2"


class DynamoClient:
    def __init__(self, client=None, table=PROPERTIES_TABLE, region=DEFAULT_REGION):
        if not client:
            self.DYNAMO_CLIENT = boto3.resource("dynamodb", region_name=region)
            self.PROPERTYSERVICE_TABLE = self.DYNAMO_CLIENT.Table(table)
        else:
            self.DYNAMO_CLIENT = client
            self.PROPERTYSERVICE_TABLE = self.DYNAMO_CLIENT.Table(table)

    def get_all_items(self, args={}):
        try:
            result = self.PROPERTYSERVICE_TABLE.scan(**args)
        except ClientError as e:
            raise Exception(
                "Failed to get items: {}".format(e.response["Error"]["Message"])
            )

        return result["Items"]

    def query_items(self, query, args={}):
        try:
            result = self.PROPERTYSERVICE_TABLE.query(
                KeyConditionExpression=query, **args
            )
        except ClientError as e:
            raise Exception(
                "Failed to get items: {}".format(e.response["Error"]["Message"])
            )

        return result["Items"]

    def post_item(self, body: PropertyServiceItem, args={}):
        try:
            self.PROPERTYSERVICE_TABLE.put_item(Item=body, **args)
        except ClientError as e:
            print(e)
            raise Exception(
                "Failed to create item: {}".format(e.response["Error"]["Message"])
            )

    def update_item(
        self,
        item_id,
        data_selector,
        update_expression="",
        expression_values={},
        args={},
    ):

        try:
            response = self.PROPERTYSERVICE_TABLE.update_item(
                Key={"itemId": item_id, "dataSelector": data_selector},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="ALL_NEW",
                **args,
            )
        except ClientError as e:
            raise Exception(
                "Failed to update item: {}".format(e.response["Error"]["Message"])
            )

        return response["Attributes"]

    def delete_item(self, item_id, data_selector, args={}):
        try:
            response = self.PROPERTYSERVICE_TABLE.delete_item(
                Key={
                    "itemId": item_id,
                    "dataSelector": data_selector,
                },
                ReturnValues="ALL_OLD",
                **args,
            )
            print(response)
        except ClientError as e:
            raise Exception(
                "Failed to delete item: {}".format(e.response["Error"]["Message"])
            )

        return response["Attributes"]

    def batch_delete(self, item_id, args={}):
        pass
