from os import stat_result
from models.review_request_model import ReviewModel
from models.db_item import PropertyServiceItem
from utils import clean_input, get_key_hash
import re
import operator
import math


class PropertyRequestModel(PropertyServiceItem):
    def __init__(self, postcode, streetName, **details):
        self.postcode = postcode
        self.streetName = streetName

        super().__init__(self.get_item_id(), self.get_data_selector())

        self.rooms = int(details.get("rooms", 0))
        self.parking = bool(details.get("parking", False))
        self.garden = bool(details.get("garden", False))

        self.overallRating = int(details.get("overallTotal", 0))
        self.facilitiesRating = int(details.get("facilitiesTotal", 0))
        self.locationRating = int(details.get("locationTotal", 0))
        self.managementRating = int(details.get("managementTotal", 0))
        self.reviewCount = int(details.get("reviewCount", 0))

    def get_item_id(self):
        postcode_hash = self.get_postcode_hash()
        street_name_hash = self.get_street_name_hash()
        return "{}#{}".format(postcode_hash, street_name_hash)

    def get_data_selector(self):
        street_name_hash = self.get_street_name_hash()
        return "META#{}".format(street_name_hash)

    def get_postcode_hash(self):
        clean_postcode = clean_input(self.postcode)
        return get_key_hash(clean_postcode.lower())

    def get_street_name_hash(self):
        clean_street_name = clean_input(self.streetName)
        return get_key_hash(clean_street_name.lower())

    def validate_property_postcode(self):
        return (
            re.match(
                r"^([a-zA-Z]{1,2}[a-zA-Z\d]{1,2})\s(\d[a-zA-Z]{2})$", self.postcode
            )
        ) != None

    def update_property_ratings(
        self, review: ReviewModel, update_function=operator.add
    ):
        self.locationRating = self.update_rating(
            self.locationRating, review.location, update_function
        )
        self.managementRating = self.update_rating(
            self.managementRating, review.management, update_function
        )
        self.facilitiesRating = self.update_rating(
            self.facilitiesRating, review.facilities, update_function
        )

        # Increase or decrease review count
        self.reviewCount = update_function(self.reviewCount, 1)

        self.overallRating = math.floor(
            (self.locationRating + self.managementRating + self.facilitiesRating) / 3
        )

    def update_rating(self, current_rating: int, updated_rating: int, update_function):
        if update_function(self.reviewCount, 1) <= 0:
            return 0
        current_total = current_rating * self.reviewCount
        average = update_function(current_total, updated_rating) / update_function(
            self.reviewCount, 1
        )

        return math.floor(average)
