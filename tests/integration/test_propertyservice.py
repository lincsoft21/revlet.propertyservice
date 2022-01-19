import json
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

TEST_PROPERTY_POSTCODE = "AB1 2CD"
TEST_PROPERTY_STREET_NAME = "123 Steet"


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
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE, TEST_PROPERTY_POSTCODE
        )
        yield
        utils.delete_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            TEST_PROPERTY_POSTCODE,
            TEST_PROPERTY_STREET_NAME,
        )

    def test_get_properties(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties()

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data[0]["postcode"] == TEST_PROPERTY_POSTCODE
        assert len(data) == 1

    def test_get_property_by_id(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties(TEST_PROPERTY_POSTCODE)

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data[0]["postcode"] == TEST_PROPERTY_POSTCODE

    def test_get_property_with_invalid_id(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties("12345")

        assert response["statusCode"] == 404


class TestPostPropertyService:
    @pytest.fixture(scope="class", autouse=True)
    def setupClass(self, setup):
        #  Creates the test table to be used in tests.
        utils.add_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            TEST_PROPERTY_POSTCODE,
            TEST_PROPERTY_STREET_NAME,
        )
        yield
        utils.delete_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            TEST_PROPERTY_POSTCODE,
            TEST_PROPERTY_STREET_NAME,
        )

    def test_post_property(self):
        request_body = {"postcode": "1234", "streetName": "1 Test Property"}
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 200

        # Validate property creation
        test_property = utils.get_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            request_body["postcode"],
            request_body["streetName"],
        )
        assert test_property["Item"]["postcode"] == "1234"
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
        test_property = utils.get_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            request_body["postcode"],
            request_body["streetName"],
        )
        assert test_property["Item"]["postcode"] == TEST_PROPERTY_POSTCODE
        assert test_property["Item"]["streetName"] == "2 Test Property"

    # It should allow the same street with a different postcode
    def test_post_property_with_same_street(self):
        request_body = {"postcode": "YZ9 10BA", "streetName": TEST_PROPERTY_STREET_NAME}
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 200

        # Validate property creation
        test_property = utils.get_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            request_body["postcode"],
            request_body["streetName"],
        )
        assert test_property["Item"]["postcode"] == "YZ9 10BA"
        assert test_property["Item"]["streetName"] == TEST_PROPERTY_STREET_NAME

    # It should not allow the same property to be added twice
    def test_post_property_with_same_details(self):
        request_body = {
            "postcode": TEST_PROPERTY_POSTCODE,
            "streetName": TEST_PROPERTY_STREET_NAME,
        }
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(request_body)

        assert response["statusCode"] == 400


class TestPutPropertyService:
    @pytest.fixture(scope="class", autouse=True)
    def setupClass(self, setup):
        #  Creates the test table to be used in tests.
        utils.add_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            TEST_PROPERTY_POSTCODE,
            TEST_PROPERTY_STREET_NAME,
        )
        yield
        utils.delete_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            TEST_PROPERTY_POSTCODE,
            TEST_PROPERTY_STREET_NAME,
        )

    def test_put_property(self):
        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            TEST_PROPERTY_POSTCODE, TEST_PROPERTY_STREET_NAME, request_body
        )

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert int(data["rooms"]) == 4
        assert bool(data["garden"]) == False

    # Should return 400 if the details body is invalid

    # It should return 404 if the property does not exist
    def test_put_property_with_invalid_postcode(self):
        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            "5678", TEST_PROPERTY_STREET_NAME, request_body
        )

        assert response["statusCode"] == 400

    def test_put_property_with_invalid_street(self):
        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            TEST_PROPERTY_POSTCODE, "Wrong Street", request_body
        )

        assert response["statusCode"] == 400


class TestDeletePropertyService:
    @pytest.fixture(scope="class", autouse=True)
    def setupClass(self, setup):
        #  Creates the test table to be used in tests.
        utils.add_test_data(
            TEST_PROPERTYSERVICE_CLIENT.PROPERTYSERVICE_TABLE,
            TEST_PROPERTY_POSTCODE,
            TEST_PROPERTY_STREET_NAME,
        )
        yield

    def test_delete_property(self):
        response = TEST_PROPERTYSERVICE_CLIENT.delete_property(
            TEST_PROPERTY_POSTCODE, TEST_PROPERTY_STREET_NAME
        )

        assert response["statusCode"] == 200
        assert response["body"]["streetName"] == TEST_PROPERTY_STREET_NAME

    def test_delete_property_with_invalid_postcode(self):
        response = TEST_PROPERTYSERVICE_CLIENT.delete_property(
            "1234", TEST_PROPERTY_STREET_NAME
        )

        assert response["statusCode"] == 400

    def test_delete_property_with_invalid_STREET_NAME(self):
        response = TEST_PROPERTYSERVICE_CLIENT.delete_property(
            TEST_PROPERTY_POSTCODE, "Wrong Street"
        )

        assert response["statusCode"] == 400
