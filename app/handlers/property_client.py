from models.property import PropertyUpdateModel
from models.property import Property, PropertyModel, PropertyRequestModel
from responders.lambda_responder import LambdaResponder
from data.dynamo_client import DynamoClient
from boto3.dynamodb.conditions import Key, Attr
from dataclasses import asdict
import json
import utils
import operator


class RevletPropertyService:
    def __init__(self, db_client: DynamoClient, responder: LambdaResponder):
        self._dbclient = db_client
        self._responder = responder

    def get_properties_by_postcode(self, postcode_hash):
        try:
            args = {
                "FilterExpression": Key("itemID").begins_with(postcode_hash)
                & Key("dataSelector").begins_with("META-")
            }
            response = self._dbclient.get_all_items(args)
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return self._responder.return_success_response(response)

    def get_property_by_id(self, property_id):
        try:
            query = Key("itemID").eq(property_id) & Key("dataSelector").begins_with(
                "META-"
            )
            response = self._dbclient.query_items(query)
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        if len(response) == 0:
            return self._responder.return_not_found_response("Property not found")

        return_property = PropertyModel(**response[0])
        return self._responder.return_success_response(asdict(return_property))

    def post_property(self, property_input: PropertyRequestModel):
        new_property = Property(property_input)
        if not new_property.validate_item():
            return self._responder.return_invalid_request_response("Invalid property")
        args = {"ConditionExpression": "attribute_not_exists(itemID)"}

        try:
            self._dbclient.post_item(
                new_property.response_object(),
                args,
            )
        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return self._responder.return_success_response(
            "{} Created".format(new_property.property.itemID)
        )

    def update_property_details(self, update_property: PropertyUpdateModel):
        args = {
            "ConditionExpression": "attribute_exists(itemID)",
        }

        try:
            meta_key = utils.get_metadata_key_from_item_id(update_property.itemID)
            response = self._dbclient.update_item(
                update_property.itemID,
                meta_key,
                "set rooms=:r, parking=:p, garden=:g",
                {
                    ":r": int(update_property.rooms),
                    ":p": bool(update_property.parking),
                    ":g": bool(update_property.garden),
                },
                args,
            )
        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return_property = PropertyModel(**response)
        return self._responder.return_success_response(asdict(return_property))

    def update_property_ratings(
        self, reviewed_property: PropertyModel, update_function=operator.add
    ):
        try:
            put_property_args = {"ConditionExpression": "attribute_exists(itemID)"}
            response = self._dbclient.update_item(
                reviewed_property.itemID,
                reviewed_property.dataSelector,
                "set facilitiesRating=:fr, locationRating=:lr, managementRating=:mr, reviewCount=:rc, overallRating=:or",
                {
                    ":fr": int(reviewed_property.facilitiesRating),
                    ":lr": int(reviewed_property.locationRating),
                    ":mr": int(reviewed_property.managementRating),
                    ":or": int(reviewed_property.overallRating),
                    ":rc": int(reviewed_property.reviewCount),
                },
                put_property_args,
            )
        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return_property = PropertyModel(**response)
        return self._responder.return_success_response(asdict(return_property))

    def delete_property(self, property_id):
        args = {
            "ConditionExpression": "attribute_exists(itemID)",
        }

        try:
            meta_key = utils.get_metadata_key_from_item_id(property_id)
            response = self._dbclient.delete_item(property_id, meta_key, args)

        except ValueError as v:
            return self._responder.return_invalid_request_response(str(v))
        except Exception as e:
            return self._responder.return_internal_server_error_response(str(e))

        return_deleted_property = PropertyModel(**response)
        return self._responder.return_success_response(asdict(return_deleted_property))
