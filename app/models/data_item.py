from dataclasses import dataclass, field
from datetime import date


@dataclass()
class DataItem:
    itemID: str
    dataSelector: str
