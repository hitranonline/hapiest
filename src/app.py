"""
This module launches the main GUI, which should only be ran after all setup is finished
"""

import os
import sys
from urllib.error import HTTPError, URLError

from PyQt5 import QtCore, QtWidgets

from utils.log import TextReceiver
from windows.main_window import MainWindow
from worker.hapi_thread import HapiThread
from worker.hapi_worker import HapiWorker
from worker.work_request import WorkRequest
from metadata.config import Config

def obtain_apikey():
    """
    Attempts to obtain an API key from the user if there is not one in the user Config already.
    If there is no valid API key when this function is called, the user will be prompted for one
    and the program will exit.
    """
    Config.hapi_api_key = Config.hapi_api_key.strip().lower()

    from widgets.apikey_help_widget import ApiKeyHelpWidget, ApiKeyValidator

    if Config.hapi_api_key == '0000' or ApiKeyValidator.APIKEY_REGEX.match(
        Config.hapi_api_key) is None:
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
    Config.online = True

    print(f"API Key: {Config.hapi_api_key}")
    try:
        with urllib.request.urlopen(
                f"{CrossSectionApi.BASE_URL}/{CrossSectionApi.API_ROUTE}/{Config.hapi_api_key}/" \
                        f"{CrossSectionApi.XSC_META_ROUTE}"):
            pass
        return True
    except HTTPError as _:
        # An HTTP error code was given the response. This means the APIKEY was invalid
        err_msg = """
Your HAPI API key will be used on the next launch. Please restart HAPIEST.
"""
        Config.hapi_api_key = '0000'
        obtain_apikey()
        Config.rewrite_config()
    except URLError as e:
        Config.online = False
        # URL Lookup failed. Probably means there is no internet connection
        err_msg = """
You do not have a working internet connection. A working internet connection
is needed in order to use hapiest.
"""
        print(str(e))

    from widgets.error_msg_widget import ErrorMsgWidget

    app = QtWidgets.QApplication(sys.argv)
    _ = ErrorMsgWidget(err_msg, Config.online)
    app.exec_()
    sys.exit(0)


def run():
    """
    The main method starts the GUI after asking for an api key if necessary.
    """

    # Create the data folder if it doesn't exist.
    if not os.path.exists(Config.data_folder):
        os.makedirs(Config.data_folder)

    if len(sys.argv) > 1:
        if sys.argv[1] in {'--test', '-t'}:
            import test

            test.run_tests()
            return 0
        elif sys.argv[1] in ('--download-molecule-images', '-dmi'):
            import res_gen.image_downloader as id
            id.download_images()
            return 0
        elif sys.argv[1] in ("-gba", "--generate-broadener-availability"):
            import res_gen.generate_broadener_availability as gba
            gba.generate_availability()
            return 0
    if Config.high_dpi:
        # Enable High DPI display with PyQt5
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    # Fix for mac-based systems...
    os.environ['no_proxy'] = '*'

    ##
    # The following blocks of code verify the hapi API key is in place, and it
    # is valid. If it is not valid or in place the user will we prompted for
    # one. This code also checks for a working internet connection, as hapi
    # needs one to download data. In the future, if there is no internet
    # connection the GUI should simply disable the features that require it,
    # and there could be a periodic check for internet connection that will
    # re-enable them.

    if not verify_internet_connection_and_obtain_api_key():
        return 0

    from metadata.molecule_meta import MoleculeMeta

    WorkRequest.start_work_process()

    # Hapi is now started automatically in the work process
    # start = HapiWorker(WorkRequest.START_HAPI, {})
    # start.start() # When a start_hapi request is sent, it starts automatically.

    _ = MoleculeMeta(0)
    from metadata.xsc_meta import CrossSectionMeta

    # If the cache is expired, download a list of the cross section meta file.
    # This also populates the CrossSectionMeta.molecule_metas field.
    _ = CrossSectionMeta(0)

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.gui.adjustSize()

    TextReceiver.init(window)

    _qt_result = app.exec_()

    TextReceiver.redirect_close()
    close = HapiWorker(WorkRequest.END_WORK_PROCESS, {}, callback=None)
    close.safe_exit()
    WorkRequest.WORKER.process.join()
    HapiThread.kill_all()
    return 0