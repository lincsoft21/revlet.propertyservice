from dataclasses import asdict, dataclass
import uuid
from models.data_item import DataItem
from utils import get_key_hash
from datetime import datetime, date


@dataclass
class ReviewModel(DataItem):
    title: str
    tenancyStartDate: str
    tenancyEndDate: str
    description: str = "No Descrpition"
    location: int = 0
    facilities: int = 0
    management: int = 0

    dateCreated: str = str(date.today())


class Review:
    def __init__(self, item_id, **details):
        data_selector = self.get_data_selector()
        self.review = ReviewModel(itemID=item_id, dataSelector=data_selector, **details)

    def validate_item(self):
        return self.validate_review_tenancy_dates()

    def get_data_selector(self):
        new_uuid = (uuid.uuid4()).hex
        key_value = get_key_hash(new_uuid)

        id = "REV#{}".format(str(key_value))
        return id

    def response_object(self):
        return asdict(self.review)

    def validate_review_tenancy_dates(self):
        try:
            # Convert dates to datetime
            ts_date = datetime.strptime(self.review.tenancyStartDate, "%m-%Y").date()

            # If tenancy is still active, validate start date is in past
            if self.review.tenancyEndDate.upper() == "PRESENT":
                return date.today() > ts_date

            te_date = datetime.strptime(self.review.tenancyEndDate, "%m-%Y").date()
        except Exception as e:
            print(f"Failed to convert dates: {e}")
            return False

        if te_date > date.today():
            return False

        return te_date > ts_date
