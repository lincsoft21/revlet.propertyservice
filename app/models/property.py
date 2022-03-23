from dataclasses import asdict, dataclass
from pickletools import float8
from utils import clean_input, get_key_hash
import re
from models.data_item import DataItem
import math
import operator
from datetime import date
from pydantic import validate_arguments


@validate_arguments
@dataclass
class PropertyModel(DataItem):
    postcode: str
    streetName: str
    creator: str

    rooms: int = 0
    garden: bool = False
    parking: bool = False

    overallRating: float = 0
    locationRating: float = 0
    managementRating: float = 0
    facilitiesRating: float = 0
    reviewCount: int = 0

    lastUpdatedBy: str = ""
    dateCreated: str = str(date.today())


@dataclass
class PropertyRequestModel:
    postcode: str
    streetName: str
    creator: str

    rooms: int = 0
    garden: bool = False
    parking: bool = False


@dataclass
class PropertyUpdateModel:
    itemID: str
    rooms: int
    garden: bool
    parking: bool
    lastUpdatedBy: str


class Property:
    def __init__(self, property_input):
        if type(property_input) is PropertyRequestModel:
            item_id = self.get_item_id(
                property_input.postcode, property_input.streetName
            )
            data_selector = self.get_data_selector(property_input.streetName)

            self.property = PropertyModel(
                itemID=item_id, dataSelector=data_selector, **asdict(property_input)
            )
        else:
            property_input["itemID"] = property_input.get(
                "itemID",
                self.get_item_id(
                    property_input["postcode"], property_input["streetName"]
                ),
            )
            property_input["dataSelector"] = property_input.get(
                "dataSelector", self.get_data_selector(property_input["postcode"])
            )

            self.property = PropertyModel(**property_input)

    def get_item_id(self, postcode, street_name):
        # clean_postcode = clean_input(postcode)
        # clean_street_name = clean_input(street_name)

        postcode_hash = get_key_hash(postcode)
        street_name_hash = get_key_hash(street_name)

        return "{}#{}".format(postcode_hash, street_name_hash)

    def get_data_selector(self, street_name):
        # clean_street_name = clean_input(street_name)
        street_name_hash = get_key_hash(street_name)

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
    # def update_property_ratings(
    #     self, review: ReviewModel, update_function=operator.add
    # ):
    #     self.property.locationRating = self.update_rating(
    #         self.property.locationRating, review.location, update_function
    #     )
    #     self.property.managementRating = self.update_rating(
    #         self.property.managementRating, review.management, update_function
    #     )
    #     self.property.facilitiesRating = self.update_rating(
    #         self.property.facilitiesRating, review.facilities, update_function
    #     )

    #     # Increase or decrease review count
    #     self.property.reviewCount = update_function(self.property.reviewCount, 1)

    #     self.property.overallRating = (
    #         self.property.locationRating
    #         + self.property.managementRating
    #         + self.property.facilitiesRating
    #     ) / 3

    # def update_rating(self, current_rating: int, updated_rating: int, update_function):
    #     if update_function(self.property.reviewCount, 1) <= 0:
    #         return 0

    #     current_total = current_rating * self.property.reviewCount
    #     average = update_function(current_total, updated_rating) / update_function(
    #         self.property.reviewCount, 1
    #     )

    #     return average
