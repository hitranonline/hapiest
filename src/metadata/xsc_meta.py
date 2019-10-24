from datetime import timedelta
from typing import Any, Dict, List

from data_structures.cache import JsonCache
from metadata.molecule_meta import MoleculeMeta
from utils.hapi_api import CrossSectionApi
from utils.log import err_log


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

    # A dictionary that maps molecule id to a list of cross section meta info.
    __MOLECULE_METAS = {}

    # A set of all aliases for all molecules that have cross sections available
    __XSC_ALIASES = {}

    # A set of the common name of each molecules that have cross sections available
    __XSC_NAMES = {}

    @staticmethod
    def all_aliases() -> List[str]:
        return list(CrossSectionMeta.__XSC_ALIASES)

    @staticmethod
    def all_names_sorted_by_hitran_id() -> List[str]:
        molecules = list(filter(lambda m: m.populated, map(lambda m: MoleculeMeta(m), CrossSectionMeta.__XSC_NAMES)))
        
        return list(map(lambda m: m.name, sorted(molecules, key=lambda m: m.id)))


    @staticmethod
    def add_meta_objects(meta_objs: List[Dict]):
        def insert(meta_obj):
            ind = meta_obj['molecule_id']
            # If there is no key 'ind' in __MOLECULE_METAS and an identical
            # meta_obj hasn't already been added.
            if ind in CrossSectionMeta.__MOLECULE_METAS and meta_obj not in \
                    CrossSectionMeta.__MOLECULE_METAS[ind]:
                CrossSectionMeta.__MOLECULE_METAS[ind].append(meta_obj)
            else:
                CrossSectionMeta.__MOLECULE_METAS[ind] = [meta_obj]

        list(map(insert, meta_objs))

    @staticmethod
    def create_name_list(meta_objs: List[Dict]):
        CrossSectionMeta.__XSC_NAMES = set()
        for meta in meta_objs:
            CrossSectionMeta.__XSC_NAMES.add(MoleculeMeta(meta['molecule_id']).name)

    @staticmethod
    def create_alias_list(meta_objs: List[Dict]):
        mids = set(map(lambda m: m['molecule_id'], meta_objs))
        aliases = set()
        ambiguous_aliases = set()

        for mid in mids:
            mm = MoleculeMeta(mid)
            if not mm.populated:
                continue  # I don't think this will ever happen?

            def try_add_alias(alias_str):
                if alias_str in aliases:
                    ambiguous_aliases.add(alias_str)
                else:
                    aliases.add(alias_str)

            for alias in mm.aliases:
                try_add_alias(alias.alias)

            try_add_alias(mm.inchi)
            try_add_alias(mm.inchikey)

        for alias in ambiguous_aliases:
            aliases.remove(alias)

        CrossSectionMeta.__XSC_ALIASES = aliases

    def __init__(self, molecule_id):
        """
        :param molecule_id: HITRAN MoleculeId of the molecule to retrieve xsc
        meta data for the specified molecule.
        """

        if len(CrossSectionMeta.__MOLECULE_METAS) == 0:
            self.molecule_id = molecule_id

            self.metas = []

            self.api = CrossSectionApi()

            self.cache = JsonCache(".xscm", self.api.request_xsc_meta, timedelta(days=1.0))
            if not self.cache.ok():
                err_log("Failed to load xscm from cache.")
            else:
                xsc_meta_objects = self.cache.data()

                CrossSectionMeta.add_meta_objects(xsc_meta_objects)
                CrossSectionMeta.create_alias_list(xsc_meta_objects)
                CrossSectionMeta.create_name_list(xsc_meta_objects)

                if self.molecule_id in CrossSectionMeta.__MOLECULE_METAS:
                    self.metas = CrossSectionMeta.__MOLECULE_METAS[self.molecule_id]
        else:
            self.molecule_id = molecule_id
            if molecule_id in CrossSectionMeta.__MOLECULE_METAS:
                self.metas = CrossSectionMeta.__MOLECULE_METAS[molecule_id]
            else:
                self.metas = ()

    def molecule_id_matches(self, d: Dict[str, Any]):
        return 'molecule_id' in d and d['molecule_id'] == self.molecule_id

    def get_all_filenames(self) -> List[str]:
        return list(map(lambda x: x['filename'], self.metas))
