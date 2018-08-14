import json
import time
import urllib.request as url

from functools import reduce
from typing import Any, Union, List, Dict

from utils.metadata.config import Config


class CrossSectionRequestException(Exception):

    INVALID_API_KEY = 0
    CONNECTION_FAILED = 1
    INVALID_JSON = 2

    def __init__(self, reason: int, description: str):
        Exception.__init__(self)
        self.reason = reason
        self.description = description


class CrossSectionApi:
    """
    Cross-section parameters are explained at
    http://hitran.org/docs/cross-sections-definitions/

    ===================
    API QUERY STRUCTURE
    ===================

    BASE_URL/api/<version>/<apikey>/<objects>?[conditions]

    BASE_URL=http:/hitran.org
    version=dev
    objects=molecules|cross-sections|sources|isotopologues
    apikey can be obtained in the HITRANonline user profile page.

    ==========
    CONDITIONS
    ==========

    Condition is a set of specifyers separated by the & character:

    key1=val1&key2=val2&key3=val3

    where key=val refers to the sub-condition on the object field.

    Key consists of the parameter name and optional suffix:

    >>  name__suffix ,

    where suffixes are:

      "in"  => take all objects with given parameter parameter taking values from the comma-separated list
      "between"    =>  all objects where the parameter takes its values in the range (which is given by two comma-separated values)

    For example:

      id=10  => take only one object with id=10
      id__in=10,20,30   => take objects with id either 10, 20, or 30

    ===================
    API QUERY EXAMPLES
    ===================

    http://hitran.org/api/dev/<apikey>/molecules   # request all molecules
    http://hitran.org/api/dev/<apikey>/molecules?id=106  # request molecule with specified ID
    http://hitran.org/api/dev/<apikey>/molecules?id__in=106,107  # request molecules IDs from the list
    http://hitran.org/api/dev/<apikey>/cross-sections  # request all cross-sections
    http://hitran.org/api/dev/<apikey>/cross-sections?molecule_id=106  # request all cross-sections for the specified molecule (molecule_id is used as a ref)

    ========================================
    OBJECTS FIELDS THAT CAN BE USED IN QUERY
    ========================================

    CROSS-SECTION
        id
        molecule_id   =>  (points to molecule.id)
        source_id
        numin
        numax
        npnts
        sigma_max
        temperature
        pressure
        resolution
        resolution_units
        broadener
        filename
        valid_to
        valid_from

    MOLECULE
            id
            inchi
            inchikey
            stoichiometric_formula
            ordinary_formula
            ordinary_formula_html
            common_name

    =========================================================================
    TO GET THE DATA FOR A GIVEN CROSS-SECTION,
    USE THE "FILENAME" PARAMETER OF THE API JSON OUTPUT FOR THE CROSS-SECTION
    IN THE FOLLOWING QUERY:

    http://hitran.org/data/xsec/<filename>

    FOR EXAMPLE,

    http://hitran.org/data/xsec/HNO4_220.0_0.1_780.0-830.0_04.xsc
    """

    BASE_URL = "http://hitran.org/api/dev"
    XSC_META_ROUTE = "cross-sections"
    XSC_ROUTE = "data/xsec"

    def __init__(self):
        pass

    def request_xsc_meta(self, molecule_id: int = None) -> Union[Dict[str, Any], CrossSectionRequestException]:
        """
        requests meta data about molecule cross sections.
        :param molecule_ids: an optional parameter that, if specified, will be used to narrow down what molecules meta
                              data is retrieved for. Otherwise, meta for all available molecules is retrieved (which is
                              something like 300 molecules as of August 2018).
        :return: will return a dictionary on success, which will
        """
        uri = "{}/{}/{}".format(CrossSectionApi.BASE_URL, Config.hapi_api_key, CrossSectionApi.XSC_META_ROUTE)
        if molecule_id is not None:
                uri += "?molecule_id={}".format(str(molecule_id))
        try:
            content = url.urlopen(uri).read()

        # TODO: Add more robust error handling here
        except Exception as e:
            return CrossSectionRequestException(CrossSectionRequestException.CONNECTION_FAILED, str(e))

        try:
            parsed = json.loads(content)
        except Exception as e:
            # TODO: Add a clause here that checks the response for indications that the HAPI API KEY is invalid.
            return CrossSectionRequestException(CrossSectionRequestException.INVALID_JSON, str(e))

        return parsed

    def download_xsc(self, xsc_name: str):
        uri = "{}/{}/{}".format(CrossSectionApi.BASE_URL, CrossSectionApi.XSC_ROUTE, xsc_name)
        try:
            content = url.urlopen(uri).read()
        except Exception as e:
            return False

        try:
            with open("{}/{}".format(Config.data_folder, xsc_name), "w+") as f:
                f.write(content)
        except IOError as e:
            print("Encountered IO Error while attempting to save xsc...")
            return False

        return content
