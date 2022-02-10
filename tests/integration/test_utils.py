import json
from models.property import PropertyModel, Property
from models.review import ReviewModel
import boto3
from utils import generate_property_keys, get_key_hash, clean_input
from dataclasses import asdict


def get_event_body(body, params):
    return {"headers": {}, "queryStringParameters": params, "body": json.dumps(body)}


def get_test_property_id(test_property: PropertyModel):
    return test_property.itemID


def add_test_property(
    table: "boto3.resources.factory.dynamodb.Table", test_property: PropertyModel
):
    table.put_item(Item=asdict(test_property))


def add_test_review(
    table: "boto3.resources.factory.dynamodb.Table", test_review: ReviewModel
):
    table.put_item(Item=asdict(test_review))


def delete_test_property(
    table: "boto3.resources.factory.dynamodb.Table", test_property: PropertyModel
):
    table.delete_item(
        Key={
            "itemID": test_property.itemID,
            "dataSelector": test_property.dataSelector,
        },
    )


def get_invalid_test_hash():
    clean_value = clean_input("invalid")
    return get_key_hash(clean_value)


def get_test_property(
    table: "boto3.resources.factory.dynamodb.Table",
    test_property_postcode: str,
    test_property_street_name: str,
):
    get_property = Property(
        test_property_postcode, test_property_street_name
    )

    test_result = table.get_item(
        Key={
            "itemID": get_property.property.itemID,
            "dataSelector": get_property.property.dataSelector,
        },
    )

    return test_result
