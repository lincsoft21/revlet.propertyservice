from models.db_item import PropertyServiceItem


class PropertyResponseModel(PropertyServiceItem):
    def __init__(self, itemId, postcode, streetName, **details):
        self.itemId = itemId
        self.postcode = postcode
        self.streetName = streetName

        self.rooms = details.get("rooms", 0)
        self.parking = details.get("parking", False)
        self.garden = details.get("garden", False)

        self.overallRating = details.get("overallRating", 0)
        self.facilitiesRating = details.get("facilitieRating", 0)
        self.locationRating = details.get("locatioRating", 0)
        self.managementRating = details.get("managmentRating", 0)
