from models.db_item import PropertyServiceItem
import uuid
from utils import get_key_hash
from datetime import date, datetime


class ReviewModel(PropertyServiceItem):
    def __init__(self, itemId, **details):
        super().__init__(itemId, self.get_data_selector())

        self.title = details["title"]
        self.description = details.get("description", "No description")
        self.tenancyStartDate = details["tenancyStartDate"]
        self.tenancyEndDate = details["tenancyEndDate"]
        self.facilities = details.get("facilities", 0)
        self.location = details.get("location", 0)
        self.management = details.get("management", 0)

    def get_item_id(self):
        pass

    def get_data_selector(self):
        new_uuid = (uuid.uuid4()).hex
        key_value = get_key_hash(new_uuid)

        id = "REV#{}".format(str(key_value))
        return id

    def validate_review_tenancy_dates(self):
        try:
            # Convert dates to datetime
            ts_date = datetime.strptime(self.tenancyStartDate, "%m-%Y").date

            # If tenancy is still active, validate start date is in past
            if self.tenancyEndDate.upper() == "PRESENT":
                return date.today() > ts_date()

            te_date = datetime.strptime(self.tenancyEndDate, "%m-%Y").date
        except Exception as e:
            print(f"Failed to convert dates: {e}")
            return False

        return te_date > ts_date
