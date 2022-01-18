from uuid import UUID


def validate_property_id(propertyId: str):
    try:
        test_uuid = UUID(propertyId, version=4)
    except ValueError:
        return False
    return str(test_uuid) == propertyId


def validate_query_params(params):
    pass


def validate_property_postcode(postcode: str):
    pass


def get_lambda_response(status=200, data="", headers={}, isBase64=False):
    return {
        "isBase64Encoded": isBase64,
        "statusCode": status,
        "headers": headers,
        "body": data,
    }
