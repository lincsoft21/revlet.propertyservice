from uuid import UUID
import hashlib
import re


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


def clean_identifier(identifier):
    clean_value = re.sub(r"\W+", "", identifier)
    return clean_value.strip().replace(" ", "")


def generate_property_key(key_value, type="postcode", hash_input=True):
    clean_value = clean_identifier(key_value)

    hash_value = key_value
    if hash_input:
        hash_value = hashlib.shake_256(clean_value.encode()).hexdigest(5)

    if type == "selector":
        return "METADATA#{}".format(hash_value)
    else:
        return "PROPERTY#{}".format(hash_value)
