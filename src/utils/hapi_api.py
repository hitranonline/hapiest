"""
This module contains various API bindings to the HAPI API, since there is a fair amount of
boilerplate required
to call some of the HAPI functions saftely (specifically the networking related functions).
"""
import urllib.request as url
from typing import Union

from metadata.config import Config


class HapiApiException(Exception):
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

      "in"  => take all objects with given parameter parameter taking values from the
      comma-separated list
      "between"    =>  all objects where the parameter takes its values in the range (which is
      given by two comma-separated values)

    For example:

      id=10  => take only one object with id=10
      id__in=10,20,30   => take objects with id either 10, 20, or 30

    ===================
    API QUERY EXAMPLES
    ===================

    http://hitran.org/api/dev/<apikey>/molecules   # request all molecules
    http://hitran.org/api/dev/<apikey>/molecules?id=106  # request molecule with specified ID
    http://hitran.org/api/dev/<apikey>/molecules?id__in=106,107  # request molecules IDs from the
    list
    http://hitran.org/api/dev/<apikey>/cross-sections  # request all cross-sections
    http://hitran.org/api/dev/<apikey>/cross-sections?molecule_id=106  # request all
    cross-sections for the specified molecule (molecule_id is used as a ref)

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

    BASE_URL = "http://hitran.org/"
    API_ROUTE = "api/dev"
    XSC_META_ROUTE = "cross-sections"
    XSC_ROUTE = "data/xsec"
    MOLECULES_ROUTE = "molecules"

    def __init__(self):
        pass

    @staticmethod
    def __send_request(uri):
        try:
            content = url.urlopen(uri).read()
        # TODO: Add more robust error handling here. It could be a bad connection or a bad API key.
        except Exception as e:
            print(f'uri: {uri}')
            print(str(e))
            return HapiApiException(HapiApiException.CONNECTION_FAILED, str(e))
        return content

    def request_molecule_meta(self) -> Union[bytes, HapiApiException]:
        """
        :return: json text that contains information about every molecule in the HITRAN database.
        """
        uri = f"{CrossSectionApi.BASE_URL}/{CrossSectionApi.API_ROUTE}/{Config.hapi_api_key}" \
            f"/{CrossSectionApi.MOLECULES_ROUTE}"
        return CrossSectionApi.__send_request(uri)

    def request_xsc_meta(self, molecule_id: int = None) -> Union[bytes, HapiApiException]:
        """
        requests meta data about molecule cross sections.
        :param molecule_ids: an optional parameter that, if specified, will be used to narrow
        down what molecules meta
                              data is retrieved for. Otherwise, meta for all available molecules
                              is retrieved (which is
                              something like 400 molecules as of August 2018).
        :return: will return a dictionary on success, which will
        """
        uri = f"{CrossSectionApi.BASE_URL}/{CrossSectionApi.API_ROUTE}/" \
        f"{Config.hapi_api_key}/{CrossSectionApi.XSC_META_ROUTE}"
        return CrossSectionApi.__send_request(uri)

    def request_xsc(self, xsc_name: str, filename: str):
        """
        Attempts to download the specified cross section.
        :param xsc_name: Name of the cross section file.
        :return: returns False if something went wrong, otherwise it returns the bytes of the
        cross section.
        """
        uri = f"{CrossSectionApi.BASE_URL}/{CrossSectionApi.XSC_ROUTE}/{xsc_name}"
        print(uri)
        try:
            content = url.urlopen(uri).read()
        except Exception as e:
            print(str(e))
            return None

        try:
            with open("{}/{}".format(Config.data_folder, filename), "w+b") as f:
                f.write(content)
        except IOError as e:
            print(f'Encountered IO Error while attempting to save xsc: {str(e)}')
            return None

        return content
