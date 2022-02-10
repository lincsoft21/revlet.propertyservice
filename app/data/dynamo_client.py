from models.data_item import DataItem
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


class DynamoClient:
    def __init__(self, table, region="eu-west-2", args={}):
        self.DYNAMO_CLIENT = boto3.resource("dynamodb", region_name=region, **args)
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
            raise Exception("Failed to query item")

        return result["Items"]

    def post_item(self, body: DataItem, args={}):
        try:
            self.PROPERTYSERVICE_TABLE.put_item(Item=body, **args)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ValueError("Item already exists")
            raise Exception("Failed to create new item")

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
                Key={"itemID": item_id, "dataSelector": data_selector},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="ALL_NEW",
                **args,
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ValueError("Item does not exist")
            raise Exception("Failed to update item")

        return response["Attributes"]

    def delete_item(self, item_id, data_selector, args={}):
        try:
            response = self.PROPERTYSERVICE_TABLE.delete_item(
                Key={
                    "itemID": item_id,
                    "dataSelector": data_selector,
                },
                ReturnValues="ALL_OLD",
                **args,
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ValueError("Item does not exist")
            raise Exception("Failed to delete item")

        return response["Attributes"]

    def batch_delete(self, item_id, args={}):
        pass
