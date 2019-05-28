import os
import re
import sys
from urllib.error import URLError, HTTPError

if sys.version_info < (3, 6):
    print(f"You must have Python 3 installed to use hapiest - current version is {str(sys.version)}")
    sys.exit(0)

# If someone launches the program through the command 'python3 __main__.py'
# this moves the current working directory to the proper place
srcre = re.compile('.+src\\Z')
if srcre.match(os.getcwd()):
    os.chdir('..')

from windows.main_window import *
from worker.hapi_worker import *
from worker.work_request import *
from worker.hapi_thread import HapiThread
from multiprocessing import freeze_support

# Create the data folder if it doesn't exist.
if not os.path.exists(Config.data_folder):
    os.makedirs(Config.data_folder)

# This is not necessary right now but will be helpful of the behavior of
# the QApplication needs to be modified.
class App(QtWidgets.QApplication):
    def __init__(self, *args):
        QtWidgets.QApplication.__init__(self, *args)


def obtain_apikey():
    """
    Attempts to obtain an API key from the user if there is not one in the user Config already.
    If there is no valid API key when this function is called, the user will be prompted for one
    and the program will exit.
    """
    Config.hapi_api_key = Config.hapi_api_key.strip().lower()

    from widgets.apikey_help_widget import ApiKeyHelpWidget, ApiKeyValidator
    if Config.hapi_api_key == '0000' or ApiKeyValidator.APIKEY_REGEX.match(Config.hapi_api_key) is None:
        app = App(sys.argv)
        _ = ApiKeyHelpWidget()
        app.exec_()


def verify_internet_connection():
    """
    This function also verifies that the supplied hapi api key is valid. If the api key is not valid, then the value in
    the config (in memory and on disk) is overwritten and the obtain_apikey function is called, which will prompt the user for a
    valid API key and close the program.
    :return: True if there is an internet connection, false otherwise.
    """
    import urllib.request
    from utils.api import CrossSectionApi
    try:
        with urllib.request.urlopen(
                f"{CrossSectionApi.BASE_URL}/{CrossSectionApi.API_ROUTE}/{Config.hapi_api_key}/{CrossSectionApi.XSC_META_ROUTE}"):
            pass
        return True
    except HTTPError as e:
        # An HTTP error code was given the response. This means the APIKEY was invalid
        err_msg = """
Your HAPI API key is invalid. Hapiest will close after you hit Ok, and will \
prompt you for your hapi API key upon the next launch. If you think your HAPI \ 
is valid, please file a bug  report at https://github.com/hitranonline/hapiest
"""
        Config.hapi_api_key = '0000'
        obtain_apikey()
        Config.rewrite_config() 
    except URLError as e:
        # URL Lookup failed. Probably means there is no internet connection
        err_msg = """
You do not have a working internet connection. A working internet connection \
is needed in order to use hapiest.
"""

    from widgets.error_msg_widget import ErrorMsgWidget
    app = App(sys.argv)
    _ = ErrorMsgWidget(err_msg)
    app.exec_()
    sys.exit(0)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        import test
        test.run_tests()
        return

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

    obtain_apikey()
    if not verify_internet_connection():
        return 0

    from utils.metadata.molecule import MoleculeMeta

    WorkRequest.start_work_process()
    
    # Hapi is now started automatically in the work process
    # start = HapiWorker(WorkRequest.START_HAPI, {})
    # start.start() # When a start_hapi request is sent, it starts automatically.

    # 
    _ = MoleculeMeta(0)
    from utils.xsc import CrossSectionMeta
    # If the cache is expired, download a list of the cross section meta file.
    # This also populates the CrossSectionMeta.molecule_metas field.
    _ = CrossSectionMeta(0)

    app = App(sys.argv)

    window = MainWindow()
    window.gui.adjustSize()

    TextReceiver.init(window)

    qt_result = app.exec_()

    TextReceiver.redirect_close()
    close = HapiWorker(WorkRequest.END_WORK_PROCESS, {}, callback=None)
    close.safe_exit()
    WorkRequest.WORKER.process.join()
    HapiThread.kill_all()
    sys.exit(0)


if __name__ == '__main__':
    freeze_support()
    try:
        main()
    except Exception as e:
        debug(e)
