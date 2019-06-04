from datetime import timedelta
from typing import Dict, List, Union, Optional

from data_structures.cache import JsonCache
from utils.hapi_api import CrossSectionApi


class Alias:

    def __init__(self, alias, type):
        self.alias = alias
        self.type = type


class MoleculeMeta:
    __MOLECULE_METADATA: List[Dict] = None

    __FORMULA_TO_MID: Dict[str, int] = None

    __NAME_TO_MID: Dict[str, int] = None

    # A dictonary that maps a string alias to a molecule id.
    __ALIAS_TO_MID = None

    # All aliases
    __ALL_ALIASES = None

    @staticmethod
    def __initialize_molecule_metadata():
        api = CrossSectionApi()
        cache = JsonCache(".molm", api.request_molecule_meta, timedelta(days=1))
        if cache.ok():
            data = cache.data()
        else:
            return

        MoleculeMeta.__FORMULA_TO_MID = {}
        MoleculeMeta.__MOLECULE_METADATA = {}
        MoleculeMeta.__NAME_TO_MID = {}
        MoleculeMeta.__ALIAS_TO_MID = {}
        MoleculeMeta.__ALL_ALIASES = set()

        ambiguous_aliases = set()

        for molecule in data:
            mid = molecule['id']
            MoleculeMeta.__NAME_TO_MID[molecule['common_name']] = mid
            MoleculeMeta.__FORMULA_TO_MID[molecule['ordinary_formula']] = mid
            MoleculeMeta.__MOLECULE_METADATA[molecule['id']] = molecule

            aliases = set(map(lambda d: d['alias'], molecule['aliases']))
            aliases.update((molecule['ordinary_formula'], molecule['common_name']))


            def try_add_alias(alias_str):
                MoleculeMeta.__ALL_ALIASES.add(alias_str)
                if alias_str in MoleculeMeta.__ALIAS_TO_MID:
                    # Since this is ambiguous it cant be used to map to the molecule ID (which is
                    # completely unique).
                    ambiguous_aliases.add(alias_str)
                else:
                    MoleculeMeta.__ALIAS_TO_MID[alias_str] = mid

            for alias in aliases:
                try_add_alias(alias)

            try_add_alias(molecule['inchikey'])
            try_add_alias(molecule['inchi'])

        for alias in ambiguous_aliases:
            MoleculeMeta.__ALL_ALIASES.remove(alias)
            del MoleculeMeta.__ALIAS_TO_MID[alias]

    @staticmethod
    def all_names() -> List[str]:
        return list(MoleculeMeta.__NAME_TO_MID.keys())

    @staticmethod
    def all_aliases() -> List[str]:
        return list(MoleculeMeta.__ALL_ALIASES)

    @staticmethod
    def alias_to_mid(alias) -> Optional[int]:
        if alias in MoleculeMeta.__ALIAS_TO_MID:
            return MoleculeMeta.__ALIAS_TO_MID[alias]
        else:
            return None

    @staticmethod
    def all_formulas() -> List[str]:
        return list(MoleculeMeta.__FORMULA_TO_MID.keys())

    def __init__(self, molecule_id: Union[int, str]):
        if MoleculeMeta.__MOLECULE_METADATA is None:
            MoleculeMeta.__initialize_molecule_metadata()
        if type(molecule_id) == str:
            if molecule_id in MoleculeMeta.__ALIAS_TO_MID:
                molecule_id = MoleculeMeta.__ALIAS_TO_MID[molecule_id]
        if molecule_id in MoleculeMeta.__MOLECULE_METADATA:
            self.populated = True
            self.mmd = MoleculeMeta.__MOLECULE_METADATA[molecule_id]
            self.inchi = self.mmd['inchi']
            self.inchikey = self.mmd['inchikey']
            self.aliases = list(map(lambda a: Alias(**a), self.mmd['aliases']))
            self.formula = self.mmd['ordinary_formula']
            self.html = self.mmd['ordinary_formula_html']
            self.name = self.mmd['common_name']
            self.id = self.mmd['id']
        else:
            self.populated = False

    def is_populated(self):
        return self.populated
