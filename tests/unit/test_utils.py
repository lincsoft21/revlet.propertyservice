from uuid import uuid4
import hashlib
from utils import validate_id

TEST_ID = hashlib.shake_256("AB1 2CD".encode()).hexdigest(5)


class TestValidateId:
    def test_valid_id(self):
        result = validate_id(TEST_ID)

        assert result == True

    def test_valid_review_key(self):
        test_key = "REVIEW#{}".format(TEST_ID)
        print(test_key)
        result = validate_id(test_key, id_type="REVIEW")

        assert result == True

    def test_invalid_id(self):
        result = validate_id("1234")

        assert result == False

    def test_invalid_id_type(self):
        valid_id = "REVIEW#{}".format(TEST_ID)
        result = validate_id(valid_id, id_type="INVALID")

        assert result == False


## Add unit tests for property postcode validation
