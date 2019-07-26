import json
import hapi

from metadata.molecule_meta import MoleculeMeta


class ParameterAvailability:
    __AVAILABILITY = None

    __PARAMETER_GROUP_REQUIREMENTS = None

    __PARAMETER_BLACKLIST = {".par", "160-char", "par_line", "statep", "statepp"}
                             # "delta_co2", "delta_he", "delta_h2"}  # empty set for now
    __PARAMETER_GROUP_BLACKLIST = set()

    # Since case matters when querying HITRAN, we'll use lowercase all the time
    # except here, where we will fix casing for HITRAN compliant
    # HAPI uses lowercase names for already downloaded data :(\
    __PARAMETER_HITRAN_FIX = {
        "gamma_co2": "gamma_CO2",
        "gamma_h2": "gamma_H2",
        "gamma_he": "gamma_He",
        "gamma_h2o": "gamma_H2O",
        "delta_h2o": "delta_H2O",
        "delta_he": "delta_He",
        "delta_h2": "delta_H2",
        "delta_co2": "delta_CO2",
        "n_h2o": "n_H2O",
        "n_he": "n_He",
        "n_h2": "n_H2",
        "n_co2": "n_CO2",

    }

    @staticmethod
    def hitran_parameter_fix(params):
        def fix(param):
            if param in ParameterAvailability.__PARAMETER_HITRAN_FIX:
                return ParameterAvailability.__PARAMETER_HITRAN_FIX[param]
            else:
                return param

        return list(map(fix, params))

    @staticmethod
    def create_parameter_group_requirements():
        ParameterAvailability.__PARAMETER_GROUP_REQUIREMENTS = {}

        for group, req_params in hapi.PARAMETER_GROUPS.items():
            if len(req_params) == 0:
                continue

            ParameterAvailability.__PARAMETER_GROUP_REQUIREMENTS[group] = set(req_params)

    @staticmethod
    def load_availability():
        with open("res/parameters/availability.json") as f:
            contents = f.read()
        ParameterAvailability.__AVAILABILITY = json.loads(contents)
        keys = {k for k in ParameterAvailability.__AVAILABILITY}
        for k in keys:
            ParameterAvailability.__AVAILABILITY[int(k)] = ParameterAvailability.__AVAILABILITY[k]

    def __init__(self, molecule):
        if ParameterAvailability.__PARAMETER_GROUP_REQUIREMENTS is None:
            ParameterAvailability.create_parameter_group_requirements()

        if ParameterAvailability.__AVAILABILITY is None:
            ParameterAvailability.load_availability()

        self.molecule = MoleculeMeta(molecule)
        if self.molecule.populated:
            if self.molecule.id in ParameterAvailability.__AVAILABILITY:
                self.available_parameters = \
                    set(ParameterAvailability.__AVAILABILITY[self.molecule.id])
            else:
                self.available_parameters = set()
        else:
            self.available_parameters = set()

    def parameter_groups(self):
        groups = {k for k in ParameterAvailability.__PARAMETER_GROUP_REQUIREMENTS}

        for group, reqs in ParameterAvailability.__PARAMETER_GROUP_REQUIREMENTS.items():
            for req in reqs:
                if req not in self.available_parameters:
                    groups.remove(group)
                    break
                if req in ParameterAvailability.__PARAMETER_BLACKLIST:
                    groups.remove(group)
                    break

        for group in ParameterAvailability.__PARAMETER_GROUP_BLACKLIST:
            if group in groups:
                groups.remove(group)

        return groups

    def parameters(self):
        parameters = set(map(str.lower, self.available_parameters))

        for param in ParameterAvailability.__PARAMETER_BLACKLIST:
            if param in parameters:
                parameters.remove(param)

        return set(ParameterAvailability.hitran_parameter_fix(parameters))
