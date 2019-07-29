from enum import Enum


class GraphType(Enum):
    ABSORPTION_SPECTRUM = 0
    TRANSMITTANCE_SPECTRUM = 1
    RADIANCE_SPECTRUM = 2
    ABSORPTION_COEFFICIENT = 3
    BANDS = 4
    XSC = 5
