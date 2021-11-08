import boto3

DYNAMO_DB = boto3.resource("dynamodb")
PROPERTIES_TABLE = DYNAMO_DB.Table("properties")


def get_property(event, context):
    response = PROPERTIES_TABLE.get_item(Item={"PropertyId": event["id"]})
    if "Item" in response:
        return response["Item"]
    else:
        return {"statusCode": "404", "body": "Not found"}


def post_property(event, context):
    print(PROPERTIES_TABLE.table_status)

    # Use update_item if record already exists
    response = PROPERTIES_TABLE.put_item(
        Item={
            "PropertyId": event["id"],
            "Postcode": event["postcode"],
            "StreetName": event["streetName"],
        }
    )

    return {
        "statusCode": response["ResponseMetadata"]["HTTPStatusCode"],
        "body": "Proeprty " + event["id"] + " created",
    }
