import json
from uuid import uuid4
import boto3


def get_event_body(body, params):
    return {"headers": {}, "queryStringParameters": params, "body": json.dumps(body)}


def add_test_data(
    table: "boto3.resources.factory.dynamodb.Table",
    test_property_id: str = None,
    test_data=None,
):
    if not test_property_id:
        test_property_id = str(uuid4())

    if not test_data:
        test_data = {
            "propertyId": test_property_id,
            "dataSelector": "METADATA#{}".format(test_property_id),
            "postcode": "1234",
        }

    table.put_item(
        Item=test_data,
    )


def get_test_data(
    table: "boto3.resources.factory.dynamodb.Table", test_property_id: str
):

    test_result = table.get_item(
        Key={
            "propertyId": test_property_id,
            "dataSelector": "METADATA#{}".format(test_property_id),
        },
    )

    return test_result


def get_all_test_data(table: "boto3.resources.factory.dynamodb.Table"):
    test_result = table.scan()

    return test_result


def delete_test_data(
    table: "boto3.resources.factory.dynamodb.Table", test_property_id: str
):
    table.delete_item(
        Key={
            "propertyId": test_property_id,
            "dataSelector": "METADATA#{}".format(test_property_id),
        },
    )
