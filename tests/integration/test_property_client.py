import json
import os
from models.property import PropertyRequestModel, PropertyUpdateModel, Property
from responders.lambda_responder import LambdaResponder
import boto3
import pytest
import test_utils
from data.dynamo_client import DynamoClient
from handlers.property_client import RevletPropertyService

ddb_client = boto3.client(
    "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-2"
)

TEST_TABLE_NAME = "revlet-propertyservice-{}-db".format(
    os.environ.get("REVLET_ENV", "property-local")
)
db_client = DynamoClient(
    TEST_TABLE_NAME, "eu-west-2", {"endpoint_url": "http://localhost:8000"}
)
test_responder = LambdaResponder()
TEST_PROPERTYSERVICE_CLIENT = RevletPropertyService(db_client, test_responder)

TEST_PROPERTY_DETAILS = PropertyRequestModel("AB1 2CD", "123 Street", "user-1")
TEST_PROPERTY = Property(TEST_PROPERTY_DETAILS)


@pytest.fixture(scope="session", autouse=True)
def setup():
    db_client.DYNAMO_CLIENT.create_table(
        TableName=TEST_TABLE_NAME,
        AttributeDefinitions=[
            {"AttributeName": "itemID", "AttributeType": "S"},
            {"AttributeName": "dataSelector", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "itemID", "KeyType": "HASH"},
            {"AttributeName": "dataSelector", "KeyType": "RANGE"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    test_utils.add_test_property(
        TEST_PROPERTYSERVICE_CLIENT._dbclient.PROPERTYSERVICE_TABLE,
        TEST_PROPERTY.property,
    )
    yield TEST_PROPERTYSERVICE_CLIENT._dbclient.PROPERTYSERVICE_TABLE
    ddb_client.delete_table(TableName=TEST_TABLE_NAME)


class TestGetPropertyService:
    def test_get_properties_by_postcode(self):
        postcode_hash = TEST_PROPERTY.property.itemID.split("#")[0]
        response = TEST_PROPERTYSERVICE_CLIENT.get_properties_by_postcode(postcode_hash)

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data[0]["postcode"] == TEST_PROPERTY_DETAILS.postcode
        assert len(data) == 1

    def test_get_properties_by_id(self):
        response = TEST_PROPERTYSERVICE_CLIENT.get_property_by_id(
            TEST_PROPERTY.property.itemID
        )

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data["postcode"] == TEST_PROPERTY_DETAILS.postcode
        assert data["streetName"] == TEST_PROPERTY_DETAILS.streetName

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
    def setup(self):
        self.TEST_POST_PROPERTY = PropertyRequestModel(
            "TE1 2ST", "1 Test Property", "Test User"
        )

    def test_post_property(self):
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(self.TEST_POST_PROPERTY)

        assert response["statusCode"] == 200

        # Validate property creation
        test_property = test_utils.get_test_property(
            TEST_PROPERTYSERVICE_CLIENT._dbclient.PROPERTYSERVICE_TABLE,
            self.TEST_POST_PROPERTY,
        )
        assert test_property["Item"]["postcode"] == "TE1 2ST"
        assert test_property["Item"]["streetName"] == "1 Test Property"

    # It should allow creation of property with same postcode
    def test_post_property_with_same_postcode(self):
        self.TEST_POST_PROPERTY.postcode = TEST_PROPERTY_DETAILS.postcode
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(self.TEST_POST_PROPERTY)

        assert response["statusCode"] == 200

        # Validate property creation
        test_property = test_utils.get_test_property(
            TEST_PROPERTYSERVICE_CLIENT._dbclient.PROPERTYSERVICE_TABLE,
            self.TEST_POST_PROPERTY,
        )
        assert test_property["Item"]["postcode"] == TEST_PROPERTY_DETAILS.postcode
        assert test_property["Item"]["streetName"] == self.TEST_POST_PROPERTY.streetName

    # It should allow the same street with a different postcode
    def test_post_property_with_same_street(self):
        self.TEST_POST_PROPERTY.streetName = TEST_PROPERTY_DETAILS.streetName
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(self.TEST_POST_PROPERTY)

        assert response["statusCode"] == 200

        # Validate property creation
        test_property = test_utils.get_test_property(
            TEST_PROPERTYSERVICE_CLIENT._dbclient.PROPERTYSERVICE_TABLE,
            self.TEST_POST_PROPERTY,
        )
        assert test_property["Item"]["postcode"] == self.TEST_POST_PROPERTY.postcode
        assert test_property["Item"]["streetName"] == TEST_PROPERTY_DETAILS.streetName

    # It should not allow the same property to be added twice
    def test_post_property_with_same_details(self):
        self.TEST_POST_PROPERTY.postcode = TEST_PROPERTY_DETAILS.postcode
        self.TEST_POST_PROPERTY.streetName = TEST_PROPERTY_DETAILS.streetName
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(self.TEST_POST_PROPERTY)

        assert response["statusCode"] == 400

    # It should not allow property with same details with difference casing
    def test_post_property_with_same_details_different_casing(self):
        self.TEST_POST_PROPERTY.postcode = TEST_PROPERTY_DETAILS.postcode.lower()
        self.TEST_POST_PROPERTY.streetName = TEST_PROPERTY_DETAILS.streetName.lower()
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(self.TEST_POST_PROPERTY)

        assert response["statusCode"] == 400

    def test_post_property_with_invalid_postcode(self):
        self.TEST_POST_PROPERTY.postcode = "12345"
        response = TEST_PROPERTYSERVICE_CLIENT.post_property(self.TEST_POST_PROPERTY)

        assert response["statusCode"] == 400


class TestPutPropertyService:
    def setup(self):
        self.TEST_PUT_PROPERTY = PropertyUpdateModel(
            TEST_PROPERTY.property.itemID, 4, False, True, "user-2"
        )

    def test_put_property(self):
        request_body = {"rooms": 4, "parking": True, "garden": False}
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            self.TEST_PUT_PROPERTY
        )

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert int(data["rooms"]) == 4
        assert bool(data["garden"]) == False

    def test_put_property_with_property_that_does_not_exist(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        property_id = "{}#{}".format(invalid_hash, invalid_hash)

        request_body = {"rooms": 4, "parking": True, "garden": False}
        self.TEST_PUT_PROPERTY.itemID = property_id
        response = TEST_PROPERTYSERVICE_CLIENT.update_property_details(
            self.TEST_PUT_PROPERTY
        )

        assert response["statusCode"] == 400


class TestDeletePropertyService:
    def test_delete_property(self):
        response = TEST_PROPERTYSERVICE_CLIENT.delete_property(
            TEST_PROPERTY.property.itemID,
        )

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data["streetName"] == TEST_PROPERTY_DETAILS.streetName

    def test_delete_property_with_property_that_does_not_exist(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        property_id = "{}#{}".format(invalid_hash, invalid_hash)

        response = TEST_PROPERTYSERVICE_CLIENT.delete_property(property_id)

        assert response["statusCode"] == 400
