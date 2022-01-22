from app.utils import generate_review_id, generate_review_key
import utils
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

PROPERTIES_TABLE = "revlet-dev-properties"
DEFAULT_REGION = "eu-west-2"


class RevletReviewService:
    def __init__(self, client=None, table=PROPERTIES_TABLE, region=DEFAULT_REGION):
        if not client:
            self.DYNAMO_CLIENT = boto3.resource("dynamodb", region_name=region)
        else:
            self.DYNAMO_CLIENT = client

        self.PROPERTYSERVICE_TABLE = self.DYNAMO_CLIENT.Table(table)

    def get_reviews(self, p, s):
        property_key = utils.generate_property_key(p, s)
        try:
            response = self.PROPERTYSERVICE_TABLE.query(
                IndexName="ReviewIndex",
                KeyConditionExpression=Key("reviewIndexPK").eq(property_key),
            )
        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        return utils.get_lambda_response(
            200, json.dumps(response["Items"], default=str)
        )

    def post_review(self, body):
        if not "postcode" in body or not "streetName" in body:
            return utils.get_lambda_response(400, "Must specify property details")

        # Get all current reviews for the property
        reviews = self.get_reviews(body["postcode"], body["streetName"])
        if reviews["statusCode"] != 200:
            return utils.get_lambda_response(400, reviews["body"])

        # Calculate new overall rating for property
        reviews = json.loads(reviews["body"])
        property_overall = utils.get_property_overall_rating(reviews.append(body))

        property_id = utils.generate_property_key_hash(body["postcode"])
        data_selector = utils.generate_property_key_hash(body["streetName"], "selector")
        property_key = "{}#{}".format(property_id, data_selector)

        # Create ID for reivew
        review_id = generate_review_key()

        # Merge with index fields
        body.update(
            {
                "propertyId": review_id,
                "dataSelector": review_id,
                "reviewIndexPK": property_key,
                "reviewIndexSK": review_id,
            }
        )

        try:
            self.PROPERTYSERVICE_TABLE.put_item(
                Item=body,
                ConditionExpression="attribute_not_exists(propertyId)",
            )

            # Update average review for property
            self.PROPERTYSERVICE_TABLE.update_item(
                Key={
                    "propertyId": property_id,
                    "dataSelector": data_selector,
                },
                ConditionExpression="attribute_exists(propertyId)",
                UpdateExpression="set overallRating=:or",
                ExpressionAttributeValues={
                    ":or": float(property_overall),
                },
            )
        except ClientError as e:
            return utils.get_lambda_response(400, e.response["Error"]["Message"])

        return utils.get_lambda_response(200, "{} Created".format(review_id))


    def delete_review(self, id):
      review_key = generate_review_key(id)
      try:
          response = self.PROPERTYSERVICE_TABLE.delete_item(
              Key={
                  "propertyId": review_key,
                  "dataSelector": review_key,
              },
              ConditionExpression="attribute_exists(propertyId)",
              ReturnValues="ALL_OLD",
          )

      except ClientError as e:
          return utils.get_lambda_response(400, e.response["Error"]["Message"])

      return utils.get_lambda_response(
          200, json.dumps(response["Attributes"], default=str)
      )