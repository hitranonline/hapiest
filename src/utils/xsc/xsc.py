import json
import time

from utils.log import err_log
from utils.metadata.config import Config


class CrossSectionRequestException(Exception):

    INVALID_API_KEY = 0
    CONNECTION_FAILED = 1
    INVALID_JSON = 2

    def __init__(self, reason: int, description: str):
        Exception.__init__(self)
        self.reason = reason
        self.description = description

class MoleculeCrossSectionMeta:
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

    ##
    # TODO: make this proper, maybe move it to a more focal location.
    API_ROOT = "http://hitran.org/"

    def __init__(self, molecule_id):
        """
        :param molecule_id: HITRAN MoleculeId of the molecule to retrieve xsc meta data for
        """
        self.molecule_id = molecule_id

        self.metas = []

        if not self.initialize_from_cache():
            self.initialize_from_web()

    def initialize_from_cache(self):
        """
        Since the meta data is sent in JSON format it is easy to cache. See if there is a cache entry for the molecule,
        if it is check the date on it, if it is less than a day old use that otherwise fail.
        :return:
        """
        import os.path

        cache_path = '{}/.cache/xsc/'.format(Config.data_folder)

        if not os.path.exists(cache_path):
            os.mkdir(cache_path)

        molecule_cache_path = '{}/{}.xscm'.format(cache_path, str(self.molecule_id))

        if os.path.exists(molecule_cache_path) and os.path.isfile(molecule_cache_path):
            try:
                with open(molecule_cache_path, 'r') as file:
                    text = file.read() # This reads whoe whole contents of the file.
                parsed = json.loads(text)
                if time.time() > parsed['timestamp'] + 60*60*24:
                    return False
                self.metas = parsed['metas']
            except Exception as e:
                err_log("Encountered exception '{}'".format(str(e)))

        return False

    def initialize_from_web(self):
        import urllib.request as url
        try:
            content = url.urlopen("{}?apikey={}&molecule_ids={}".format(MoleculeCrossSectionMeta.API_ROOT, Config.hapi_api_key, str(self.molecule_id))).read()
        except Exception as e:
            return CrossSectionRequestException(CrossSectionRequestException.CONNECTION_FAILED, str(e))

        try:
            parsed = json.loads(content)
        except Exception as e:
            # TODO:
            # Add a clause here that checks the response for indications that the HAPI API KEY is invalid.
            return CrossSectionRequestException(CrossSectionRequestException.INVALID_JSON, str(e))

        self.metas = parsed
        try:
            path = '{}/.cache/xsc/{}.xscm'.format(Config.data_folder, str(self.molecule_id))
            with open(path, "w+") as file:
                file.write(json.dumps({
                    'timestamp': int(time.time()),
                    'metas': parsed
                }))
        except:
            pass