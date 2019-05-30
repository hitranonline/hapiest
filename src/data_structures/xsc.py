from typing import Iterable, List, Optional, Tuple

from metadata.xsc_meta import CrossSectionMeta


class CrossSection:
    """
    Represents a parsed cross section. This is just a data class so it doesn't get represented by
    a dictionary.
    """

    def __init__(self, nu: Iterable[float], abscoef: Iterable[float], step: float, numin: float,
                 numax: float, molecule: str, len: int, pressure: float, temp: float):
        self.nu = tuple(nu)
        self.abscoef = tuple(abscoef)
        self.step = step
        self.numin = numin
        self.numax = numax
        self.molecule = molecule
        self.len = len
        self.pressure = pressure
        self.temp = temp


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

        return CrossSection(x, y, step, numin, max_wavenum, molecule, num_points, pressure,
                            temperature)


class CrossSectionFilter:

    def __init__(self, molecule_id: int, wn_range: Tuple[float, float] = None,
                 pressure_range: Tuple[float, float] = None,
                 temp_range: Tuple[float, float] = None):
        self.molecule_id = molecule_id
        self.wn_range = wn_range
        self.temp_range = temp_range
        self.pressure_range = pressure_range

    def get_cross_sections(self) -> List[str]:
        if self.molecule_id not in CrossSectionMeta.molecule_metas:
            return []
        return [item['filename'] for item in CrossSectionMeta.molecule_metas[self.molecule_id] if
                self.xsc_is_conformant(item)]

    def xsc_is_conformant(self, xsc) -> bool:
        """
        :param xsc: The cross-section dict-object which this filter is
        checking.
        :return: True if the supplied cross-section satisfies all of the
        conditions of this filter, otherwise false.
        """
        return (self.pressure_range is None or (
                self.pressure_range[0] <= xsc['pressure'] <= self.pressure_range[1])) and (
                           self.temp_range is None or (
                           self.temp_range[0] <= xsc['temperature'] <= self.temp_range[1])) and (
                           self.wn_range is None or (
                           xsc['numin'] <= self.wn_range[0] and xsc['numax'] >= self.wn_range[1]))
