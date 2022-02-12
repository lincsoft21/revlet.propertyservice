from dataclasses import asdict, dataclass
import uuid
from models.data_item import DataItem
from utils import get_key_hash
from datetime import datetime, date
import operator
from models.property import PropertyModel


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


@dataclass
class ReviewRequestModel:
    title: str
    itemID: str
    creator: str
    tenancyStartDate: str
    tenancyEndDate: str
    description: str = "No Description"
    location: int = 0
    facilities: int = 0
    management: int = 0


class Review:
    def __init__(self, review):
        if type(review) is ReviewRequestModel:
            data_selector = self.get_data_selector(review.creator)
            self.review = ReviewModel(dataSelector=data_selector, **asdict(review))
        else:
            self.review = ReviewModel(**review)

    def validate_item(self):
        return self.validate_review_tenancy_dates()

    def get_data_selector(self, user):
        # Use user ID to generate review ID - limit users to 1 review per property
        key_value = get_key_hash(user)

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

    def update_property_ratings(
        self, review_property: PropertyModel, update_function=operator.add
    ):
        review_property.locationRating = self.update_rating(
            review_property.reviewCount,
            review_property.locationRating,
            self.review.location,
            update_function,
        )
        review_property.managementRating = self.update_rating(
            review_property.reviewCount,
            review_property.managementRating,
            self.review.management,
            update_function,
        )
        review_property.facilitiesRating = self.update_rating(
            review_property.reviewCount,
            review_property.facilitiesRating,
            self.review.facilities,
            update_function,
        )

        # Increase or decrease review count
        review_property.reviewCount = update_function(review_property.reviewCount, 1)

        review_property.overallRating = (
            review_property.locationRating
            + review_property.managementRating
            + review_property.facilitiesRating
        ) / 3

        return review_property

    def update_rating(
        self,
        review_count: int,
        current_rating: int,
        updated_rating: int,
        update_function,
    ):
        if update_function(review_count, 1) <= 0:
            return 0

        current_total = current_rating * review_count
        average = update_function(current_total, updated_rating) / update_function(
            review_count, 1
        )

        return average
