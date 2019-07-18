import json
import hapi

from metadata.molecule_meta import MoleculeMeta


class BroadenerAvailability:
    __AVAILABILITY = None

    __PARAMETER_MAP = {
        "gamma_h2": {"voigt_h2", "sdvoigt_h2"},
        "gamma_he": {"voigt_he", "sdvoigt_he"},
        "gamma_co2": {"voigt_co2", "sdvoigt_co2"},
        "gamma_h2o": {"voigt_h2o"}
    }

    # Since case matters when querying HITRAN, we'll use lowercase all the time
    # except here, where we will fix casing for HITRAN compliant
    # HAPI uses lowercase names for already downloaded data :(\
    __PARAM_HITRAN_FIX = {
        "gamma_co2": "gamma_CO2",
        "gamma_h2": "gamma_H2",
        "gamma_he": "gamma_He",
        "gamma_h2o": "gamma_H2O"
    }

    @staticmethod
    def hitran_parameter_fix(params):
        def fix(param):
            if param in BroadenerAvailability.__PARAM_HITRAN_FIX:
                return BroadenerAvailability.__PARAM_HITRAN_FIX[param]
            else:
                return param

        return list(map(fix, params))

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
                for p in BroadenerAvailability.__PARAMETER_MAP[req_param]:
                    groups.remove(p)

        return groups

    def parameters(self):
        parameters = set(map(str.lower, hapi.PARLIST_ALL))

        for param in BroadenerAvailability.__PARAMETER_MAP:
            if param not in self.broadeners:
                parameters.remove(param)

        return set(BroadenerAvailability.hitran_parameter_fix(parameters))
