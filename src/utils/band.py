from typing import *

class Band:
    def __init__(self, nu: List[float], sw: List[float], band_id: str):
        self.x = nu
        self.y = sw
        self.band_id = band_id

class Bands:

    def __init__(self, bands: List[Band], table_name: str = ''):
        self.table_name = table_name
        self.bands = bands.copy()
        self.use_scatter_plot = True

    def add_band(self, band: Band):
        self.bands.append(band)