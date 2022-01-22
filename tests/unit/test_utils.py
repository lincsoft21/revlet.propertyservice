from uuid import uuid4
from utils import validate_id
from uuid import uuid4


class TestValidateId:
    def test_valid_id(self):
        test_key = "AebL32ut9j"
        result = validate_id(test_key)

        assert result == True

    def test_valid_review_key(self):
        test_key = "REVIEW#AebL32ut9j"
        result = validate_id(test_key, id_type="REVIEW")

        assert result == True

    def test_invalid_id(self):
        result = validate_id("1234")

        assert result == False

    def test_invalid_id_type(self):
        valid_id = "REVIEW#AebL32ut9j"
        result = validate_id(valid_id, id_type="INVALID")

        assert result == False


## Add unit tests for property postcode validation
