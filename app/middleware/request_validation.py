from models.review import ReviewRequestModel
from models.property import PropertyUpdateModel
from models.property import PropertyRequestModel
import re


class RequestValidator:
    def validate_authenticated_user(self, context):
        if "user" in context:
            return context["user"]

        return None

    def validate_property_request(self, request_body, user):
        try:
            new_property = PropertyRequestModel(creator=user, **request_body)
        except Exception as e:
            ## Log something here
            return None

        return new_property

    def validate_review_request(self, request_body, author):
        try:
            new_review = ReviewRequestModel(creator=author, **request_body)
        except Exception as e:
            return None

        return new_review

    def validate_property_update_request(self, id, request_body, user):
        try:
            update_property = PropertyUpdateModel(
                itemID=id, lastUpdatedBy=user, **request_body
            )
        except Exception as e:
            ## Log something here
            return None

        return update_property

    def validate_property_id(property_id):
        result = re.match(r"^\w{10}#\w{10}$", property_id)
        return result != None

    def validate_review_key(review_key):
        result = re.match(r"^REV#\w{10}$", review_key)
        return result != None