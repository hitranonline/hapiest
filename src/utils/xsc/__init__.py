import json
import time
from typing import List, Optional, Any, Dict, Tuple

from utils.log import err_log
from utils.metadata.config import Config
from utils.xsc.api import CrossSectionApi


class CrossSectionMolecules:
    FROM_MID = {}
    FROM_NAME = {}
    FROM_HTML = {}
    MOLECULES = []

    PATH = "res/xsc/molecules.json"

    @staticmethod
    def init():
        try:
            with open(CrossSectionMolecules.PATH, "r") as file:
               contents = file.read()
            molecules = json.loads(contents)
            CrossSectionMolecules.MOLECULES = molecules
        except Exception as e:
            print("Encountered error '{}' while initializing CrossSectionMolecules".format(str(e)))
            return

        for molecule in molecules:
            CrossSectionMolecules.FROM_MID[molecule['id']] = molecule
            CrossSectionMolecules.FROM_NAME[molecule['ordinary_formula']] = molecule
            CrossSectionMolecules.FROM_HTML[molecule['ordinary_formula_html']] = molecule

    @staticmethod
    def molecule_id_to_name(molecule_id: int) -> Optional[str]:
        if molecule_id not in CrossSectionMolecules.FROM_MID:
            return None
        else:
            return CrossSectionMolecules.FROM_MID[molecule_id]['ordinary_formula']

    @staticmethod
    def name_to_molecule_id(name: str) -> Optional[int]:
        if name not in CrossSectionMolecules.FROM_NAME:
            return None
        else:
            return CrossSectionMolecules.FROM_NAME[name]['id']

    @staticmethod
    def all_names() -> List[str]:
        return list(CrossSectionMolecules.FROM_NAME.keys())

    @staticmethod
    def all_molecules() -> List[str]:
        return list(CrossSectionMolecules.MOLECULES)


class CrossSectionMeta:
    """
    This class represents meta data about all of a molecules available
    cross-sections. It can cache to disk in the '{data}/.cache/xsc/' folder to prevent
    unneeded web requests, since they're slow. If the data is not present on
    the disk, it will be downloaded automatically.

    The cached cross section metas have the 'xscm' file extension and contain plain json
    in the following format:

    {
        // This is an unix time-stamp that is used to put an
        // expiration date on the cached data, so it will rarely
        // be out-dated.
        'timestamp': 143145,
        // This is an array of 'metas.' Each meta corresponds to
        // an actual cross-section file that is available to download on hitran.org
        'metas':    [   {
                        "__identity__": "id",
                        "numax": 811.995,
                        "pressure": 757.7,
                        "id": 139,
                        "molecule_id": 104,
                        "numin": 750.0028,
                        "valid_from": "2000-05-04",
                        "temperature": 296.7,
                        "sigma_max": 4.867e-18,
                        "npnts": 6173,
                        "__class__": "CrossSection",
                        "valid_to": "2012-12-31",
                        "filename": "CCl4_296.7K-757.7Torr_750.0-812.0_00.xsc",
                        "resolution_units": "cm-1",
                        "source_id": 631,
                        "resolution": 0.03,
                        "broadener": "air"
                        },
                        ...
                    ]
    }

    """

    molecule_metas = {}

    def __init__(self, molecule_id):
        """
        :param molecule_id: HITRAN MoleculeId of the molecule to retrieve xsc meta data for
        """
        self.molecule_id = molecule_id

        self.metas = []

        self.api = CrossSectionApi()

        # initialization basically means assigning CrossSectionMeta.all_metas a valid value
        if str(molecule_id) not in CrossSectionMeta.molecule_metas and not self.initialize_from_cache():
            if not self.initialize_from_web():
                raise Exception("Failed to download xsc metadata for molecule_id = {}".format(self.molecule_id))

        if self.molecule_id in CrossSectionMeta.molecule_metas:
            self.metas = CrossSectionMeta.molecule_metas[self.molecule_id]

    def molecule_id_matches(self, d: Dict[str, Any]):
        return 'molecule_id' in d and d['molecule_id'] == self.molecule_id

    def get_all_filenames(self) -> List[str]:
        return list(map(lambda x: x['filename'], self.metas))

    def initialize_from_cache(self):
        """
        Since the meta data is sent in JSON format it is easy to cache. See if there is a cache entry for the molecule,
        if it is check the date on it, if it is less than a day old use that otherwise fail.
        :return:
        """
        import os.path

        cache_path = '{}/.cache/'.format(Config.data_folder)
        xsc_cache_path = '{}/xsc'.format(cache_path)
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
            os.mkdir(xsc_cache_path)
            return False

        molecule_cache_path = '{}/cache.xscm'.format(xsc_cache_path, self.molecule_id)

        if os.path.exists(molecule_cache_path) and os.path.isfile(molecule_cache_path):
            try:
                with open(molecule_cache_path, 'r') as file:
                    text = file.read()  # This reads whole contents of the file.
                parsed = json.loads(text)
                # It has been more than 24 hours since this cached file was retrieved, returning false will re-retrieve
                # it.
                if int(time.time()) > parsed['timestamp'] + 60*60*24:
                    return False
                self.add_meta_objects(parsed['metas'])
            except Exception as e:
                err_log("Encountered exception '{}'".format(str(e)))
                return False

        return True

    def initialize_from_web(self):
        res = self.api.request_xsc_meta()  # This will fetch meta data about every cross section
        if type(res) == list:
            self.add_meta_objects(res)
        else:
            return False
        try:
            path = '{}/.cache/xsc/cache.xscm'.format(Config.data_folder, str(self.molecule_id))
            with open(path, "w+") as file:
                file.write(json.dumps({
                    'timestamp': int(time.time()),
                    'metas': res
                }))
        except Exception as e:
            print("Failed to write to CrossSectionMeta cache: {}".format(str(e)))
            return False
        return True

    def add_meta_objects(self, meta_objs: List[Dict]):
        def insert(meta_obj):
            ind = meta_obj['molecule_id']
            if ind in CrossSectionMeta.molecule_metas:
                CrossSectionMeta.molecule_metas[ind].append(meta_obj)
            else:
                CrossSectionMeta.molecule_metas[ind] = [meta_obj]

        list(map(insert, meta_objs))


class CrossSectionFilter:

    def __init__(self, molecule_id: int, wn_range: Tuple[float, float] = None, pressure_range: Tuple[float, float] = None,
                 temp_range: Tuple[float, float] = None):
        self.molecule_id = molecule_id
        self.wn_range = wn_range
        self.temp_range = temp_range
        self.pressure_range = pressure_range

    def get_cross_sections(self) -> List[str]:
        if self.molecule_id not in CrossSectionMeta.molecule_metas:
            return []
        return list(item['filename'] for item in CrossSectionMeta.molecule_metas[self.molecule_id] if self.passes(item))

    def passes(self, meta) -> bool:
        return (self.pressure_range is None or (self.pressure_range[0] < meta['pressure'] < self.pressure_range[1])) \
                and (self.temp_range is None or (self.temp_range[0] < meta['temperature'] < self.temp_range[1])) \
                and (self.wn_range is None or (meta['numin'] < self.wn_range[0] and meta['numax'] > self.wn_range[1]))
