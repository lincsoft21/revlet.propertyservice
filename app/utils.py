import hashlib
import re
import uuid


def validate_query_params(param, event):
    if not "queryStringParameters" in event:
        return False

    if not param in event["queryStringParameters"]:
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
    clean_value = re.sub(r"[a-z0-9-]", "", identifier)
    return clean_value.strip().replace(" ", "-")


def get_key_hash(key):
    updated = (key.lower()).replace(" ", "-")
    # Replace all spaces with - then hash
    return hashlib.shake_256(updated.encode()).hexdigest(5)


def validate_hash(key):
    result = re.match(r"^\w{10}$", key)
    return result != None


def validate_property_id(id):
    result = re.match(r"^\w{10}#\w{10}$", id)
    return result != None


def validate_review_key(key):
    result = re.match(r"^REV#\w{10}$", key)
    return result != None


def get_metadata_key_from_item_id(id):
    key_hashes = id.split("#")
    return "META#{}".format(key_hashes[1])


def generate_property_key_hash(hash_value, key="PROPERTY"):
    if not validate_hash(hash_value):
        raise Exception("Invalid hash value")

    clean_value = clean_input(hash_value)
    if not key in ["PROPERTY", "METADATA", "REVIEW"]:
        raise Exception({"message": "Invalid key type"})

    return "{}#{}".format(key.upper(), clean_value)


def generate_property_keys(postcode_hash, street_name_hash=None):
    key_map = {"itemID": "", "dataSelector": "", "reviewIndexPK": ""}

    key_map["itemID"] = generate_property_key_hash(postcode_hash)

    if street_name_hash:
        key_map["dataSelector"] = generate_property_key_hash(
            street_name_hash, "METADATA"
        )
        key_map["reviewIndexPK"] = "{}#{}".format(
            key_map["itemID"], key_map["dataSelector"]
        )

    return key_map


def generate_review_key(id=None):
    if id == None:
        new_uuid = (uuid.uuid4()).hex
        id = get_key_hash(new_uuid)
    return "REVIEW#{}".format(str(id))


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
