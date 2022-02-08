import json
import os
from models.property_request_model import PropertyRequestModel
import boto3
import pytest
import test_utils
from dynamo_client import DynamoClient
from property_client import RevletPropertyService

ddb_client = boto3.client(
    "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-2"
)
ddb = boto3.resource(
    "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-2"
)

TEST_TABLE_NAME = "revlet-propertyservice-{}-db".format(
    os.environ.get("REVLET_ENV", "property-local")
)
db_client = DynamoClient(TEST_TABLE_NAME, "eu-west-2", {"endpoint_url": "http://localhost:8080"})
TEST_PROPERTYSERVICE_CLIENT = RevletPropertyService(db_client)

TEST_PROPERTY_POSTCODE = "AB1 2CD"
TEST_PROPERTY_STREET_NAME = "123 Steet"
TEST_PROPERTY = PropertyRequestModel(TEST_PROPERTY_POSTCODE, TEST_PROPERTY_STREET_NAME)


@pytest.fixture(scope="session", autouse=True)
def setup():
    ddb.create_table(
        TableName=TEST_TABLE_NAME,
        AttributeDefinitions=[
            {"AttributeName": "itemId", "AttributeType": "S"},
            {"AttributeName": "dataSelector", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "itemId", "KeyType": "HASH"},
            {"AttributeName": "dataSelector", "KeyType": "RANGE"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    test_utils.add_test_property(
        TEST_PROPERTYSERVICE_CLIENT.DBClient.PROPERTYSERVICE_TABLE, TEST_PROPERTY
    )
    yield TEST_PROPERTYSERVICE_CLIENT.DBClient.PROPERTYSERVICE_TABLE
    ddb_client.delete_table(TableName=TEST_TABLE_NAME)


class TestGetPropertyService:
    def test_get_properties_by_postcode(self):
        postcode_hash = TEST_PROPERTY.itemId.split("#")[0]
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties_by_postcode(postcode_hash)

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data[0]["postcode"] == TEST_PROPERTY_POSTCODE
        assert len(data) == 1

    def test_get_properties_by_id(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_property_by_id(TEST_PROPERTY.itemId)

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data["postcode"] == TEST_PROPERTY_POSTCODE
        assert data["streetName"] == TEST_PROPERTY_STREET_NAME

    def test_get_properties_by_postcode_with_invalid_postcode(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties_by_postcode("12345")

        assert response["statusCode"] == 400

    def test_get_property_by_id_with_invalid_values(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_property_by_id("12345")

        assert response["statusCode"] == 400

    def test_get_property_by_id_that_does_not_exist(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        invalid_property_id = "{}#{}".format(invalid_hash, invalid_hash)
        response = TEST_PROPERTYSERVICE_CLIENT.get_property_by_id(invalid_property_id)

        assert response["statusCode"] == 404


class TestPostPropertyService:
    def test_post_property(self):
        request_body = {"postcode": "TE1 2ST", "streetName": "1 Test Property"}
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 200

        # Validate property creation
        test_property = test_utils.get_test_property(
            TEST_PROPERTYSERVICE_CLIENT.DBClient.PROPERTYSERVICE_TABLE,
            request_body["postcode"],
            request_body["streetName"],
        )
        assert test_property["Item"]["postcode"] == "TE1 2ST"
        assert test_property["Item"]["streetName"] == "1 Test Property"

    # It should allow creation of property with same postcode
    def test_post_property_with_same_postcode(self):
        request_body = {
            "postcode": TEST_PROPERTY_POSTCODE,
            "streetName": "2 Test Property",
        }
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 200

        # Validate property creation
        test_property = test_utils.get_test_property(
            TEST_PROPERTYSERVICE_CLIENT.DBClient.PROPERTYSERVICE_TABLE,
            request_body["postcode"],
            request_body["streetName"],
        )
        assert test_property["Item"]["postcode"] == TEST_PROPERTY_POSTCODE
        assert test_property["Item"]["streetName"] == "2 Test Property"

    # It should allow the same street with a different postcode
    def test_post_property_with_same_street(self):
        request_body = {"postcode": "YZ9 1BA", "streetName": TEST_PROPERTY_STREET_NAME}
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 200

        # Validate property creation
        test_property = test_utils.get_test_property(
            TEST_PROPERTYSERVICE_CLIENT.DBClient.PROPERTYSERVICE_TABLE,
            request_body["postcode"],
            request_body["streetName"],
        )
        assert test_property["Item"]["postcode"] == "YZ9 1BA"
        assert test_property["Item"]["streetName"] == TEST_PROPERTY_STREET_NAME

    # It should not allow the same property to be added twice
    def test_post_property_with_same_details(self):
        request_body = {
            "postcode": TEST_PROPERTY_POSTCODE,
            "streetName": TEST_PROPERTY_STREET_NAME,
        }
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 400

    # It should not allow property with same details with difference casing
    def test_post_property_with_same_details_different_casing(self):
        test_postcode = TEST_PROPERTY_POSTCODE.lower()
        test_street = TEST_PROPERTY_STREET_NAME.lower()
        request_body = {
            "postcode": test_postcode,
            "streetName": test_street,
        }
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 400

    def test_post_property_with_invalid_postcode(self):
        request_body = {"postcode": "12345", "streetName": TEST_PROPERTY_STREET_NAME}
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 400


class TestPutPropertyService:
    def test_put_property(self):
        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            TEST_PROPERTY.itemId,
            request_body,
        )

        print(response)
        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert int(data["rooms"]) == 4
        assert bool(data["garden"]) == False

    # Should return 400 if the details body is invalid

    # It should return 404 if the property does not exist
    def test_put_property_with_invalid_id(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            invalid_hash, request_body
        )

        assert response["statusCode"] == 400
        assert response["body"] == "Invalid property ID"

    def test_put_property_with_property_that_does_not_exist(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        property_id = "{}#{}".format(invalid_hash, invalid_hash)

        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            property_id, request_body
        )

        assert response["statusCode"] == 400


class TestDeletePropertyService:
    def test_delete_property(self):
        response = TEST_PROPERTYSERVICE_CLIENT.delete_property(
            TEST_PROPERTY.itemId,
        )

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data["streetName"] == TEST_PROPERTY_STREET_NAME

    def test_delete_property_with_invalid_id(self):
        response = TEST_PROPERTYSERVICE_CLIENT.delete_property("1234")

        assert response["statusCode"] == 400

    def test_delete_property_with_property_that_does_not_exist(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        property_id = "{}#{}".format(invalid_hash, invalid_hash)

        response = TEST_PROPERTYSERVICE_CLIENT.delete_property(property_id)

        assert response["statusCode"] == 400
