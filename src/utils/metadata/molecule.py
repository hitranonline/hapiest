from datetime import timedelta
from typing import Dict, List, Union

from utils.api import CrossSectionApi
from utils.cache import JsonCache


class MoleculeMeta:

    __MOLECULE_METADATA: List[Dict] = None

    __FORMULA_TO_MID: Dict[str, int] = None

    @staticmethod
    def __initialize_molecule_metadata():
        api = CrossSectionApi()
        cache = JsonCache(".molm", api.request_molecule_meta, timedelta(days=1))
        if cache.ok():
            data = cache.data()
        MoleculeMeta.__FORMULA_TO_MID = {}
        MoleculeMeta.__MOLECULE_METADATA = {}

        for molecule in data:
            MoleculeMeta.__FORMULA_TO_MID[molecule['ordinary_formula']] = molecule['id']
            MoleculeMeta.__MOLECULE_METADATA[molecule['id']] = molecule

    @staticmethod
    def all_names() -> List[str]:
        return list(MoleculeMeta.__FORMULA_TO_MID.keys())

    def __init__(self, molecule_id: Union[int, str]):
        if MoleculeMeta.__MOLECULE_METADATA is None:
            MoleculeMeta.__initialize_molecule_metadata()

        if type(molecule_id) == str and molecule_id in MoleculeMeta.__FORMULA_TO_MID:
            molecule_id = MoleculeMeta.__FORMULA_TO_MID[molecule_id]
        if molecule_id in MoleculeMeta.__MOLECULE_METADATA:
            self.populated = True
            self.mmd = MoleculeMeta.__MOLECULE_METADATA[molecule_id]
            self.inchi = self.mmd['inchi']
            self.inchikey = self.mmd['inchikey']
            self.aliases = self.mmd['aliases']
            self.formula = self.mmd['ordinary_formula']
            self.html = self.mmd['ordinary_formula_html']
            self.id = self.mmd['id']
        else:
            self.populated = False


    def is_populated(self):
        return self.populated

    def all_formulas(self) -> List[str]:
        return list(MoleculeMeta.__FORMULA_TO_MID.keys())