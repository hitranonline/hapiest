from typing import *

class Band:
    def __init__(self, x: List[float], y: List[float], band_id: str):
        self.x = x
        self.y = y
        self.band_id = band_id

class Bands:

    def __init__(self, bands: List[Band], table_name: str):
        self.table_name = table_name
        self.bands = bands
