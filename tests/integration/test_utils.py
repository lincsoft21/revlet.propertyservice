import json
from uuid import uuid4
import boto3
from utils import generate_property_key


def get_event_body(body, params):
    return {"headers": {}, "queryStringParameters": params, "body": json.dumps(body)}


def add_test_data(
    table: "boto3.resources.factory.dynamodb.Table",
    test_property_postcode: str = None,
    test_property_street_name: str = None,
    test_data=None,
):
    if not test_property_postcode:
        test_property_postcode = "AB1 2CD"

    if not test_property_street_name:
        test_property_street_name = "123 Street"

    pk = generate_property_key(test_property_postcode)
    sk = generate_property_key(test_property_street_name, "selector")

    if not test_data:
        test_data = {
            "propertyId": pk,
            "dataSelector": sk,
            "postcode": test_property_postcode,
            "streetName": test_property_street_name,
            "reviewIndexPK": "{}#{}".format(pk, sk),
            "reviewIndexSK": sk,
        }
    else:
        test_data.update(
            {
                "propertyId": pk,
                "dataSelector": sk,
                "reviewIndexPK": "{}#{}".format(pk, sk),
                "reviewIndexSK": sk,
            }
        )

    table.put_item(
        Item=test_data,
    )


def get_test_data(
    table: "boto3.resources.factory.dynamodb.Table",
    test_property_postcode: str,
    test_property_street_name: str,
):
    pk = generate_property_key(test_property_postcode)
    sk = generate_property_key(test_property_street_name, "selector")

    test_result = table.get_item(
        Key={
            "propertyId": pk,
            "dataSelector": sk,
        },
    )

    return test_result


def get_all_test_data(table: "boto3.resources.factory.dynamodb.Table"):
    test_result = table.scan()
    return test_result


def delete_test_data(
    table: "boto3.resources.factory.dynamodb.Table",
    test_property_postcode: str,
    test_property_street_name: str,
):
    table.delete_item(
        Key={
            "propertyId": test_property_postcode,
            "dataSelector": "METADATA#{}".format(test_property_street_name),
        },
    )
