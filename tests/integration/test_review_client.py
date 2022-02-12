import json
import os
from datetime import date
from models.review import ReviewRequestModel
from models.property import PropertyRequestModel
from responders.lambda_responder import LambdaResponder
import boto3
import pytest
import test_utils
from handlers.review_client import RevletReviewService
from data.dynamo_client import DynamoClient
from models.property import Property
from models.review import Review

ddb_client = boto3.client(
    "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-2"
)

TEST_TABLE_NAME = "revlet-propertyservice-{}-db".format(
    os.environ.get("REVLET_ENV", "review-local")
)

db_client = DynamoClient(
    TEST_TABLE_NAME, "eu-west-2", {"endpoint_url": "http://localhost:8000"}
)
test_responder = LambdaResponder()

TEST_CLIENT = RevletReviewService(db_client, test_responder)

# Test Property
# TEST_PROPERTY_POSTCODE = "AB1 2CD"
# TEST_PROPERTY_STREET_NAME = "123 Steet"
# TEST_PROPERTY = Property(TEST_PROPERTY_POSTCODE, TEST_PROPERTY_STREET_NAME)

TEST_PROPERTY_DETAILS = PropertyRequestModel("AB1 2CD", "123 Street", "user-1")
TEST_PROPERTY = Property(TEST_PROPERTY_DETAILS)

# Test Review
TEST_REVIEW_DETAILS = ReviewRequestModel(
    "Test Review",
    TEST_PROPERTY.property.itemID,
    "user-1",
    "06-2020",
    "PRESENT",
    3,
    3,
    3,
)
TEST_REVIEW = Review(TEST_REVIEW_DETAILS)


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
        TEST_CLIENT._dbclient.PROPERTYSERVICE_TABLE, TEST_PROPERTY.property
    )
    test_utils.add_test_review(
        TEST_CLIENT._dbclient.PROPERTYSERVICE_TABLE, TEST_REVIEW.review
    )
    yield TEST_CLIENT._dbclient.PROPERTYSERVICE_TABLE
    ddb_client.delete_table(TableName=TEST_TABLE_NAME)


class TestGetReviewService:
    def test_get_all_reviews(self):
        response = TEST_CLIENT.get_reviews(TEST_PROPERTY.property.itemID)

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data[0]["title"] == TEST_REVIEW_DETAILS.title
        assert len(data) == 1

    def test_get_review_with_property_that_does_not_exist(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        invalid_property_id = "{}#{}".format(invalid_hash, invalid_hash)
        response = TEST_CLIENT.get_reviews(invalid_property_id)

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert len(data) == 0

    def test_get_review_with_invalid_id(self):
        response = TEST_CLIENT.get_reviews("12345")

        assert response["statusCode"] == 400
        assert response["body"] == "Invalid property ID"


class TestPostReviewService:
    def setup(self):
        self.TEST_POST_REVIEW = ReviewRequestModel(
            "Test Post Review",
            TEST_PROPERTY.property.itemID,
            "user-2",
            "06-2020",
            "PRESENT",
            3,
            3,
            3,
        )

    def test_post_review(self):
        response = TEST_CLIENT.post_review(self.TEST_POST_REVIEW)

        assert response["statusCode"] == 200

    def test_post_review_with_invalid_property_key(self):
        self.TEST_POST_REVIEW.itemID = test_utils.get_invalid_test_hash()
        response = TEST_CLIENT.post_review(self.TEST_POST_REVIEW)

        assert response["statusCode"] == 400

    def test_post_review_for_property_that_does_not_exist(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        self.TEST_POST_REVIEW.itemID = "{}#{}".format(invalid_hash, invalid_hash)
        response = TEST_CLIENT.post_review(self.TEST_POST_REVIEW)

        assert response["statusCode"] == 404

    def test_post_review_with_invalid_tenancy_dates(self):
        self.TEST_POST_REVIEW.tenancyEndDate = "01-1999"
        response = TEST_CLIENT.post_review(self.TEST_POST_REVIEW)

        assert response["statusCode"] == 400

    def test_post_review_with_same_user(self):
        self.TEST_POST_REVIEW.creator = TEST_PROPERTY.property.creator
        response = TEST_CLIENT.post_review(self.TEST_POST_REVIEW)

        assert response["statusCode"] == 400


class TestDeleteReviewService:
    def test_delete_review(self):
        response = TEST_CLIENT.delete_review(
            TEST_PROPERTY.property.itemID,
            TEST_REVIEW.review.dataSelector,
        )

        data = json.loads(response["body"])
        assert response["statusCode"] == 200
        assert data["title"] == TEST_REVIEW_DETAILS.title

    def test_delete_review_that_does_not_exist(self):
        invalid_hash = test_utils.get_invalid_test_hash()
        response = TEST_CLIENT.delete_review(
            TEST_PROPERTY.property.itemID, invalid_hash
        )

        assert response["statusCode"] == 400
