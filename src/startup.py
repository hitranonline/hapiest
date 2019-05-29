"""
This is the startup module. It has the utility function
verify_internet_connection_and_obtain_api_key. When this package is imported, it moves the
current working directory to the proper place, if necessary.
"""
import os
import re
import sys
from urllib.error import HTTPError, URLError

from PyQt5 import QtWidgets


if sys.version_info < (3, 6):
    print(f"You must have Python 3 installed to use hapiest, current version is {str(sys.version)}")
    sys.exit(0)

# If someone launches the program through the command 'python3 __main__.py'
# this moves the current working directory to the proper place
SRC_REGEX = re.compile('.+src\\Z')
if SRC_REGEX.match(os.getcwd()):
    os.chdir('..')

from metadata.config import Config


def obtain_apikey():
    """
    Attempts to obtain an API key from the user if there is not one in the user Config already.
    If there is no valid API key when this function is called, the user will be prompted for one
    and the program will exit.
    """
    Config.hapi_api_key = Config.hapi_api_key.strip().lower()

    from widgets.apikey_help_widget import ApiKeyHelpWidget, ApiKeyValidator

    if Config.hapi_api_key == '0000' or \
            ApiKeyValidator.APIKEY_REGEX.match(Config.hapi_api_key) is None:
        app = QtWidgets.QApplication(sys.argv)
        _ = ApiKeyHelpWidget()
        app.exec_()


def verify_internet_connection_and_obtain_api_key():
    """
    This function also verifies that the supplied hapi api key is valid. If the api key is not
    valid, then the value in the config (in memory and on disk) is overwritten and the
    obtain_apikey function is called, which will prompt the user for a valid API key and close the
    program.
    :return: True if there is an internet connection, false otherwise.
    """
    import urllib.request
    from utils.hapi_api import CrossSectionApi

    try:
        with urllib.request.urlopen(
                f"{CrossSectionApi.BASE_URL}/{CrossSectionApi.API_ROUTE}/{Config.hapi_api_key}" \
                f"{CrossSectionApi.XSC_META_ROUTE}"):
            pass
        return True
    except HTTPError as _:
        # An HTTP error code was given the response. This means the APIKEY was invalid
        err_msg = """
Your HAPI API key is invalid, or you did not enter one. Hapiest will close after you hit Ok, and
will prompt you for your hapi API key upon the next launch. If you think your HAPI is valid,
please file a bug report at https://github.com/hitranonline/hapiest
"""
        Config.hapi_api_key = '0000'
        obtain_apikey()
        Config.rewrite_config()
    except URLError as _:
        # URL Lookup failed. Probably means there is no internet connection
        err_msg = """
You do not have a working internet connection. A working internet connection
is needed in order to use hapiest.
"""

    from widgets.error_msg_widget import ErrorMsgWidget

    app = QtWidgets.QApplication(sys.argv)
    _ = ErrorMsgWidget(err_msg)
    app.exec_()
    sys.exit(0)
