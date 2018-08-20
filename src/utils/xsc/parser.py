import sys

from typing import Optional

from utils.xsc import CrossSection


class XscParser:
    """
    Parses '.xsc' files according to the specification that can be found here:
    http://hitran.org/docs/cross-sections-definitions/
    """

    @staticmethod
    def parse(data: str) -> Optional[CrossSection]:
        lines = data.splitlines()

        header = lines[0]
        lines = lines[1:]

        molecule = header[0:20].strip()
        numin = float(header[20:30].strip())
        max_wavenum = float(header[30:40].strip())
        num_points = int(header[40:47].strip())
        temperature = float(header[47:54].strip())
        pressure = float(header[54:60].strip())
        _max_crossvalue = header[60:70].strip()
        _instrument_res = header[70:75].strip()
        _common_name = header[75:90].strip()
        _reserved = header[90:94].strip()
        _broadener = header[94:97].strip()
        _reference = header[97:100].strip()

        y = []

        for line in lines:
            for yvalue in line.split():
                y.append(float(yvalue))
        step = (max_wavenum - numin) / float(num_points)
        x = list(map(lambda n: numin + float(n) * step, range(0, num_points)))

        return CrossSection(x, y, step, numin, max_wavenum, molecule, num_points, pressure, temperature)
