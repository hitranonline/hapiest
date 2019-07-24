from typing import *

from hapi import *
from utils.hapiest_util import *
from utils.log import log


MoleculeId = int
IsotopologueId = int
GlobalIsotopologueId = int
IsoName = AnyStr


class IsotopologueMeta:
    """
     Static members.
     Data scraped using the scrape.js function.
     The first element in the tuple is the minimum wave number to get data, and the
     second is the maximum wave number.
    """
    MOLECULE_DATA_RANGE: Dict[MoleculeId, Tuple[float, float]] = {1: (8.400e-5, 25710.825),
        2:                                                           (0.757, 14075.298),
        3:                                                           (0.026, 6996.681),
        4:                                                           (0.791, 10363.675),
        5:                                                           (3.402, 14477.377),
        6:                                                           (0.001, 11501.872),
        7:                                                           (6.440e-7, 17272.060),
        8:                                                           (1.000e-6, 9273.214),
        9:                                                           (0.017, 4092.948),
        10:                                                          (0.498, 3074.153),
        11:                                                          (0.058, 10348.719),
        12:                                                          (0.007, 1769.982),
        13:                                                          (0.003, 35874.955),
        14:                                                          (13.620, 32351.592),
        15:                                                          (5.342, 20231.245),
        16:                                                          (7.656, 16033.492),
        17:                                                          (5.888, 13907.689),
        18:                                                          (0.015, 1207.639),
        19:                                                          (0.396, 7821.109),
        20:                                                          (1.000e-6, 3099.958),
        21:                                                          (1.081, 3799.682),
        22:                                                          (11.541, 9354.200),
        23:                                                          (0.015, 17585.789),
        24:                                                          (0.873, 3197.961),
        25:                                                          (0.043, 1730.371),
        26:                                                          (1.983, 9889.038),
        27:                                                          (225.045, 3000.486),
        28:                                                          (1.901e-6, 3601.652),
        29:                                                          (686.731, 2001.348),
        30:                                                          (580.000, 996.000),
        31:                                                          (2.985, 11329.780),
        32:                                                          (10.018, 1889.334),
        33:                                                          (0.173, 3675.819),
        34:                                                          (68.716, 158.303),
        35:                                                          (763.641, 797.741),
        36:                                                          (3.976, 2530.462),
        37:                                                          (0.155, 315.908),
        38:                                                          (614.740, 3242.172),
        39:                                                          (0.019, 1407.206),
        40:                                                          (794.403, 1705.612),
        41:                                                          (890.052, 945.665),
        42:                                                          (582.830, 1518.016),
        43:                                                          (0.053, 1302.217),
        44:                                                          (4.360e-4, 759.989),
        45:                                                          (3.227, 36405.367),
        46:                                                          (1.532, 2585.247),
        47:                                                          (0.040, 2824.347),
        48:                                                          (200.772, 307.374),
        49:                                                          (793.149, 899.767)}

    # Indices defined in hapi
    ID_LOC: int = 0
    ISO_NAME_LOC: int = 1
    ABUNDANCE_LOC: int = 2
    MASS_LOC: int = 3
    MOL_NAME_LOC: int = 4

    # A list of all isotopologues
    all_isotopologues: List['IsotopologueMeta'] = []

    # Maps molecule id to a list of all isotopologues of that molecule
    molecules: Dict[MoleculeId, List['IsotopologueMeta']] = {}

    # Maps pointing to Isotopologue objects given name, id, global id, etc.
    # Maps molecule id to Isotopologue object for a normal molecule
    FROM_MOL_ID: Dict[MoleculeId, 'IsotopologueMeta'] = {}
    # Maps the name of an isotopologue to the Isotopologue object representing it
    FROM_ISO_NAME: Dict[str, 'IsotopologueMeta'] = {}
    # Maps the global id of an iso to the Isotopologue object representing it
    FROM_GLOBAL_ID: Dict[GlobalIsotopologueId, 'IsotopologueMeta'] = {}
    # Maps the pair (molecule_id, iso_id) to the Isotopologue object representing it
    FROM_MOL_ID_ISO_ID: Dict[Tuple[MoleculeId, IsotopologueId], 'IsotopologueMeta'] = {}
    # Maps molecule name to the Isotopologue object representing it
    FROM_MOL_NAME: Dict[str, 'IsotopologueMeta'] = {}

    # Regular expressions to create HTML from a molecules chemical definition
    # Found this on the internet
    ELEMENT_REGEX: str = 'A[cglmrstu]|B[aehikr]?|C[adeflmnorsu]?|D[bsy]?|E[rsu]|F[elmr]?|G[' \
                         'ade]|H[efgos]?|I[nr]?|Kr?|L[airuv]|M[dgnot]|N[abdeiop]?|O(s)?|P[' \
                         'abdmortu]?|R[abefghnu]|S[bcegimnr]?|T[abcehilm]|U(u[' \
                         'opst])?|V|W|Xe|Yb?|Z[nr]'
    # Regex for an isotope of the form '(12C)', e.g. the number of neutrons before the element,
    # then the periodic symbol
    ISOTOPE_REGEX: str = '\\((?P<neutrons>\\d+)(?P<iso_element>(' + ELEMENT_REGEX + '))\\)'
    # Regex for either an isotope or an element
    CHUNK_REGEX: str = '((?P<isotope>' + ISOTOPE_REGEX + ')|(?P<element>(' + ELEMENT_REGEX + \
                       ')))' + '(?P<count>\\d+)?'
    # Full regex
    ISO_TO_HTML_REGEX: re = re.compile(CHUNK_REGEX)

    @staticmethod
    def create_html(the_iso: str) -> str:
        """
        *Creates html for isotopologues on fetch window.*
        """
        iso = '%s' % the_iso
        html = ''
        start = 0

        # When it's an empty string we're done
        while iso != '':
            match = IsotopologueMeta.ISO_TO_HTML_REGEX.match(iso)

            # Our regex didn't match - meaning the string is malformed / not a valid chemical
            if not match:
                # Special case for NOp (not sure what it is though)
                if iso == '+':
                    html += iso
                    return html
                print('Error parsing isotopologue to html ' + iso)
                return iso

            # Start index of our next substring (lob off the part of the string we're using now)
            start = match.end()

            # This would cause an instant crash so avoid it if possible
            if start > len(iso):
                break

            # In the regex, we defined some groups / bound some string values - this is how they
            # get accessed
            dat = match.groupdict()
            iso = iso[start:]

            # This is an isotope - handle it as such
            if dat['neutrons'] is not None:
                html += '&nbsp;<sup>' + dat['neutrons'] + '</sup>'
                html += dat['iso_element']

            # This is a regular old element
            else:
                html += dat['element']

            # How many of the element / isotope
            if dat['count'] is not None:
                html += '<sub>' + dat['count'] + '</sub>'

        return html

    @staticmethod
    def populate():
        """
        * Creates 'Isotopologue's for each one of the isotoplogues as defined in hapi.ISO.*
        """
        for (key, _) in ISO.items():
            (mid, iid) = key
            iso = IsotopologueMeta(mid, iid)

            if mid not in IsotopologueMeta.molecules:
                IsotopologueMeta.molecules[mid] = [iso]
            else:
                IsotopologueMeta.molecules[mid].append(iso)

        for (mid, isos) in IsotopologueMeta.molecules.items():
            IsotopologueMeta.all_isotopologues.extend(isos)

    @staticmethod
    def from_molecule_name(mol_name: str) -> 'IsotopologueMeta':
        """
        *Converts a string molecule name into an Isotopologue object.*
        """
        return IsotopologueMeta.FROM_MOL_NAME[mol_name]

    @staticmethod
    def from_iso_name(iso_name: str) -> 'IsotopologueMeta':
        """
        *Converts a string Isotopologue name into an Isotopologue object.*
        """
        return IsotopologueMeta.FROM_ISO_NAME[iso_name]

    @staticmethod
    def from_molecule_id(mid: int) -> 'IsotopologueMeta':
        """
        *Converts an integer molecule id into an Isotopologue object*
        """
        return IsotopologueMeta.FROM_MOL_ID[mid]

    @staticmethod
    def from_mol_id_iso_id(mid: int, iid: int) -> 'IsotopologueMeta':
        """
        *Converts an int molecule ID and an int iso id and returns an isotopologue object.*
        """
        return IsotopologueMeta.FROM_MOL_ID_ISO_ID[(mid, iid)]

    @staticmethod
    def from_global_id(gid: int) -> 'IsotopologueMeta':
        """
        *Returns a Isotopologue object, given an integer: Global id.*
        """
        return IsotopologueMeta.FROM_GLOBAL_ID[gid]

    def get_wn_range(self) -> Tuple[float, float]:
        """
        *Returns wave number range as a tuple.*
        """
        if self.molecule_id in IsotopologueMeta.MOLECULE_DATA_RANGE:
            return IsotopologueMeta.MOLECULE_DATA_RANGE[self.molecule_id]
        else:
            log('No wavenumber range-data for molecule id ', self.molecule_id)
            return 0, 100000000

    def get_iso_count(self) -> int:
        """
        Returns the number of Isotopologues of a given molecule.
        """
        return len(IsotopologueMeta.molecules[self.molecule_id])

    def get_all_isos(self) -> List['IsotopologueMeta']:
        return IsotopologueMeta.molecules[self.molecule_id]

    def __init__(self, molecule_id: int, isotopologue_id: int):
        # This should never happen, but just in case...
        if (molecule_id, isotopologue_id) not in ISO:
            print("AAAAA" + molecule_id)
            raise Exception("Invalid isotopologue")

        # Grab data from hapi
        data = ISO[(molecule_id, isotopologue_id)]

        # Create bindings - the indices are those as defined in HAPI
        self.molecule_id = molecule_id
        self.iso_id = isotopologue_id
        self.id = data[IsotopologueMeta.ID_LOC]
        self.iso_name = data[IsotopologueMeta.ISO_NAME_LOC]
        self.abundance = data[IsotopologueMeta.ABUNDANCE_LOC]
        self.mass = data[IsotopologueMeta.MASS_LOC]
        self.molecule_name = data[IsotopologueMeta.MOL_NAME_LOC]

        # Generate html for the isotopologue
        self.html = IsotopologueMeta.create_html(self.iso_name)

        if molecule_id in IsotopologueMeta.MOLECULE_DATA_RANGE:
            self.wn_range = IsotopologueMeta.MOLECULE_DATA_RANGE[molecule_id]
            (self.numin, self.numax) = self.wn_range

        # Create mapings for conversion methods
        IsotopologueMeta.FROM_GLOBAL_ID[self.id] = self

        # Only for the normal element, which is iso_id of 1
        if isotopologue_id == 1:
            IsotopologueMeta.FROM_MOL_ID[molecule_id] = self
            IsotopologueMeta.FROM_MOL_NAME[self.molecule_name] = self

        IsotopologueMeta.FROM_ISO_NAME[self.iso_name] = self

        IsotopologueMeta.FROM_MOL_ID_ISO_ID[(molecule_id, isotopologue_id)] = self

    def iso_tuple(self):
        return self.molecule_id, self.iso_id


IsotopologueMeta.populate()
