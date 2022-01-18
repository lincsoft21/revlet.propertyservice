import json
import os
from uuid import uuid4
import boto3
import pytest
import test_utils as utils
from propertyservice_client import RevletPropertyService

ddb_client = boto3.client(
    "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-2"
)
ddb = boto3.resource(
    "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-2"
)

TEST_TABLE_NAME = "propertyservice-test-table"
TEST_PROPERTYSERVICE_CLIENT = RevletPropertyService(ddb, TEST_TABLE_NAME)
TEST_PROPERTY_ID = str(uuid4())


@pytest.fixture(scope="session", autouse=True)
def setup():
    ddb.create_table(
        TableName=TEST_TABLE_NAME,
        AttributeDefinitions=[
            {"AttributeName": "propertyId", "AttributeType": "S"},
            {"AttributeName": "dataSelector", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "propertyId", "KeyType": "HASH"},
            {"AttributeName": "dataSelector", "KeyType": "RANGE"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    yield TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE
    ddb_client.delete_table(TableName=TEST_TABLE_NAME)


class TestGetPropertyService:
    @pytest.fixture(scope="class", autouse=True)
    def setupClass(self, setup):
        #  Creates the test table to be used in tests.
        utils.add_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE, TEST_PROPERTY_ID
        )
        yield
        utils.delete_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE, TEST_PROPERTY_ID
        )

    def test_get_properties(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties()

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data[0]["postcode"] == "1234"
        assert len(data) == 1

    def test_get_property_by_id(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties(TEST_PROPERTY_ID)

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data[0]["postcode"] == "1234"

    def test_get_property_with_invalid_id(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties("12345")

        assert response["statusCode"] == 404


class TestPostPropertyService:
    def test_post_property(self):
        request_body = {"postcode": "1234", "streetName": "1 Test Property"}
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 200

        # Validate property creation
        data = json.loads(response["body"])
        test_property = utils.get_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE, data["propertyId"]
        )
        assert test_property["Item"]["postcode"] == "1234"
        assert test_property["Item"]["streetName"] == "1 Test Property"


class TestPutPropertyService:
    @pytest.fixture(scope="class", autouse=True)
    def setupClass(self, setup):
        #  Creates the test table to be used in tests.
        utils.add_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE, TEST_PROPERTY_ID
        )
        yield
        utils.delete_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE, TEST_PROPERTY_ID
        )

    def test_put_property(self):
        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            TEST_PROPERTY_ID, request_body
        )

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert int(data["rooms"]) == 4
        assert bool(data["garden"]) == False

    # Should return 400 if the details body is invalid

    # It should return 404 if the property does not exist
    def test_put_property_with_invalid_id(self):
        all_items = TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE.scan()
        print(all_items["Items"])

        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            "5678", request_body
        )

        all_items = TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE.scan()
        print(all_items["Items"])

        print(response)
        assert response["statusCode"] == 400


class TestDeletePropertyService:
    @pytest.fixture(scope="class", autouse=True)
    def setupClass(self, setup):
        test_review_data = {
            "propertyId": TEST_PROPERTY_ID,
            "dataSelector": "REVIEW#1234-5678",
            "title": "Test Review",
        }
        #  Creates the test table to be used in tests.
        utils.add_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE, TEST_PROPERTY_ID
        )

        # Add Review data to be removed with property
        utils.add_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            TEST_PROPERTY_ID,
            test_review_data,
        )
        yield

    def test_delete_property(self):
        request_body = utils.get_event_body(
            {},
            {"id": TEST_PROPERTY_ID},
        )
        response = TEST_PROPERTYSERVICE_CLIENT.delete_property(TEST_PROPERTY_ID)

        print(response)
        assert response["statusCode"] == 200
        assert response["body"] == "Property {} deleted".format(TEST_PROPERTY_ID)

    def test_delete_property_with_invalid_id(self):
        request_body = utils.get_event_body(
            {},
            {"id": "1234"},
        )
        response = TEST_PROPERTYSERVICE_CLIENT.delete_property("1234")

        assert response["statusCode"] == 404
