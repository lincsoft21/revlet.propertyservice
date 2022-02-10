from dataclasses import asdict, dataclass
from utils import clean_input, get_key_hash
import re
from models.data_item import DataItem
from models.review import ReviewModel
import math
import operator
from datetime import date
from pydantic import validate_arguments


@validate_arguments
@dataclass
class PropertyModel(DataItem):
    postcode: str
    streetName: str

    rooms: int = 0
    garden: bool = False
    parking: bool = False

    overallRating: int = 0
    locationRating: int = 0
    managementRating: int = 0
    facilitiesRating: int = 0
    reviewCount: int = 0

    dateCreated: str = str(date.today())


class Property:
    def __init__(self, postcode, streetName, **details):
        details["itemID"] = details.get(
            "itemID", self.get_item_id(postcode, streetName)
        )
        details["dataSelector"] = details.get(
            "dataSelector", self.get_data_selector(streetName)
        )

        self.property = PropertyModel(
            postcode=postcode, streetName=streetName, **details
        )

    def get_item_id(self, postcode, street_name):
        clean_postcode = clean_input(postcode)
        clean_street_name = clean_input(street_name)

        postcode_hash = get_key_hash(clean_postcode.lower())
        street_name_hash = get_key_hash(clean_street_name.lower())

        return "{}#{}".format(postcode_hash, street_name_hash)

    def get_data_selector(self, street_name):
        clean_street_name = clean_input(street_name)
        street_name_hash = get_key_hash(clean_street_name.lower())

        return "META#{}".format(street_name_hash)

    # RESPONSE
    def response_object(self):
        return asdict(self.property)

    ## PROPERTY VALIDATION
    def validate_item(self):
        return self.validate_property_postcode()

    def validate_property_postcode(self):
        return (
            re.match(
                r"^([a-zA-Z]{1,2}[a-zA-Z\d]{1,2})\s(\d[a-zA-Z]{2})$",
                self.property.postcode,
            )
        ) != None

    ## PROPERTY RATINGS
    def update_property_ratings(
        self, review: ReviewModel, update_function=operator.add
    ):
        self.property.locationRating = self.update_rating(
            self.property.locationRating, review.location, update_function
        )
        self.property.managementRating = self.update_rating(
            self.property.managementRating, review.management, update_function
        )
        self.property.facilitiesRating = self.update_rating(
            self.property.facilitiesRating, review.facilities, update_function
        )

        # Increase or decrease review count
        self.property.reviewCount = update_function(self.property.reviewCount, 1)

        self.property.overallRating = math.floor(
            (
                self.property.locationRating
                + self.property.managementRating
                + self.property.facilitiesRating
            )
            / 3
        )

    def update_rating(self, current_rating: int, updated_rating: int, update_function):
        if update_function(self.property.reviewCount, 1) <= 0:
            return 0

        current_total = current_rating * self.property.reviewCount
        average = update_function(current_total, updated_rating) / update_function(
            self.property.reviewCount, 1
        )

        return math.floor(average)
