import json
from models.property_request_model import PropertyRequestModel
from models.review_request_model import ReviewModel
import boto3
from utils import generate_property_keys, get_key_hash, clean_input


def get_event_body(body, params):
    return {"headers": {}, "queryStringParameters": params, "body": json.dumps(body)}


def get_test_property_id(test_property: PropertyRequestModel):
    return test_property.itemId


def add_test_property(
    table: "boto3.resources.factory.dynamodb.Table", test_property: PropertyRequestModel
):
    table.put_item(Item=test_property.convert_to_dictionary())


def add_test_review(
    table: "boto3.resources.factory.dynamodb.Table", test_review: ReviewModel
):
    table.put_item(Item=test_review.convert_to_dictionary())


def delete_test_property(
    table: "boto3.resources.factory.dynamodb.Table", test_property: PropertyRequestModel
):
    table.delete_item(
        Key={
            "itemId": test_property.itemId,
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
    get_property = PropertyRequestModel(
        test_property_postcode, test_property_street_name
    )

    test_result = table.get_item(
        Key={
            "itemId": get_property.itemId,
            "dataSelector": get_property.dataSelector,
        },
    )

    return test_result
