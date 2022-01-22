import hashlib
import re
import uuid


def validate_query_params(params: list, event):
    if not event["queryStringParams"]:
        return False

    for param in params:
        if not param in event["queryStringParams"]:
            return False

    return True


# Validate postcode follows UK postcode format
def validate_property_postcode(postcode: str):
    return (
        re.match(r"^([a-zA-Z]{1,2}[a-zA-Z\d]{1,2})\s(\d[a-zA-Z]{2})$", postcode)
    ) != None


def get_lambda_response(status=200, data="", headers={}, isBase64=False):
    return {
        "isBase64Encoded": isBase64,
        "statusCode": status,
        "headers": headers,
        "body": data,
    }


# Remove spaces and special characters from street names
def clean_input(identifier):
    clean_value = re.sub(r"\W+", "", identifier)
    return clean_value.strip().replace(" ", "-").lower()


def get_key_hash(key):
    return hashlib.shake_256(key.encode()).hexdigest(5)


def generate_property_key_hash(key_value, type="postcode", hash_input=True):
    clean_value = clean_input(key_value)

    hash_value = key_value
    if hash_input:
        hash_value = get_key_hash(clean_value)

    if type == "selector":
        return "METADATA#{}".format(hash_value)
    else:
        return "PROPERTY#{}".format(hash_value)


def generate_property_key(postcode, streetName):
    p_hash = generate_property_key_hash(postcode)
    s_hash = generate_property_key_hash(streetName, "selector")
    return "{}#{}".format(p_hash, s_hash)


def generate_review_key(id=None):
    if id == None:
        new_uuid = (uuid.uuid4()).hex
        id = get_key_hash(new_uuid)
    return "REVIEW#{}".format(str(id))


def get_property_overall_rating(reviews):
    if len(reviews) == 0:
        return 0

    total = 0
    for rev in range(reviews):
        total += rev["overall"]

    average = total / len(reviews)
    return round(average, 1)


def validate_id(id, id_type=None):
    result = None
    # Confirm that the ID is 10 bytes long
    if id_type == None:
        result = re.match(r"^\w{10}$", id)
        return result != None

    if id_type.upper() not in ["REVIEW", "PROPERTY", "METADATA"]:
        return False

    # Given an ID type, validate
    regex_string = r"^" + id_type.upper() + r"#\w{10}$"
    return (re.match(regex_string, id)) != None
