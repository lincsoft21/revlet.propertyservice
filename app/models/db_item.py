import re
import utils
from datetime import date


class PropertyServiceItem:
    def __init__(self, property_id, data_selector):
        self.itemId = property_id
        self.dataSelector = data_selector
        self.dateCreated = str(date.today())

    def get_item_id(self):
        pass

    def get_data_selector(self):
        pass

    def convert_to_dictionary(self):
        return dict(
            (key, value)
            for key, value in self.__dict__.items()
            if not callable(value) and not key.startswith("__")
        )
