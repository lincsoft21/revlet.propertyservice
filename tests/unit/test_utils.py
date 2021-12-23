from uuid import uuid4
from utils import validate_property_id
from uuid import uuid4


class TestValidatePropertyId:
    def test_valid_id(self):
        test_uuid = uuid4()
        result = validate_property_id(str(test_uuid))

        assert result == True

    def test_invalid_id(self):
        result = validate_property_id("1234")

        assert result == False


## Add unit tests for property postcode validation
