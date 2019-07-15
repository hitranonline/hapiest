import json
import hapi

from metadata.molecule_meta import MoleculeMeta


class BroadenerAvailability:
    __AVAILABILITY = None

    __PARAMETER_MAP = {
        "gamma_H2": "voigt_h2",
        "gamma_He": "voigt_he",
        "gamma_CO2": "voigt_co2",
    }

    @staticmethod
    def load_availability():
        with open("res/broadeners/availability.json") as f:
            contents = f.read()
        BroadenerAvailability.__AVAILABILITY = json.loads(contents)
        keys = {k for k in BroadenerAvailability.__AVAILABILITY}
        for k in keys:
            BroadenerAvailability.__AVAILABILITY[int(k)] = BroadenerAvailability.__AVAILABILITY[k]

    def __init__(self, molecule):
        if BroadenerAvailability.__AVAILABILITY is None:
            BroadenerAvailability.load_availability()

        self.molecule = MoleculeMeta(molecule)
        if self.molecule.populated:
            if self.molecule.id in BroadenerAvailability.__AVAILABILITY:
                self.broadeners = set(BroadenerAvailability.__AVAILABILITY[self.molecule.id])
            else:
                self.broadeners = set()
        else:
            self.broadeners = set()

    def parameter_groups(self):
        groups = {k for k in hapi.PARAMETER_GROUPS} # start with all parameters

        for req_param in BroadenerAvailability.__PARAMETER_MAP:
            if req_param not in self.broadeners:
                groups.remove(BroadenerAvailability.__PARAMETER_MAP[req_param])

        return groups

    def parameters(self):
        parameters = set(hapi.PARLIST_ALL)

        for param in BroadenerAvailability.__PARAMETER_MAP:
            if param not in self.broadeners:
                parameters.remove(param)

        return parameters
