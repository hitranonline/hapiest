"""
This is the main module. It basically checks that there is a hapi api key, asks for one if there
is not one, and launches the main GUI. Thats about it.
"""
import os
import sys
from multiprocessing import freeze_support

from PyQt5 import QtWidgets, QtCore

# This should be imported first: it verifies the correct python version is running, and moves the
# current working directory to wherever it ought to be. Importing things for their side-effects
# is probably bad practice, but so is using python.
from startup import verify_internet_connection_and_obtain_api_key

from windows.main_window import MainWindow
from worker.hapi_worker import HapiWorker
from worker.work_request import WorkRequest
from worker.hapi_thread import HapiThread
from utils.metadata.config import Config
from utils.log import TextReceiver

# Create the data folder if it doesn't exist.
if not os.path.exists(Config.data_folder):
    os.makedirs(Config.data_folder)

# This is not necessary right now but will be helpful of the behavior of
# the QApplication needs to be modified.
# class App(QtWidgets.QApplication):
#    def __init__(self, *args):
#        QtWidgets.QApplication.__init__(self, *args)

def main():
    """
    The main method starts the GUI after asking for an api key if necessary.
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        import test
        test.run_tests()
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

    from utils.metadata.molecule import MoleculeMeta

    WorkRequest.start_work_process()

    # Hapi is now started automatically in the work process
    # start = HapiWorker(WorkRequest.START_HAPI, {})
    # start.start() # When a start_hapi request is sent, it starts automatically.

    _ = MoleculeMeta(0)
    from utils.metadata.xsc import CrossSectionMeta
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
    sys.exit(0)
    return 0

if __name__ == '__main__':
    freeze_support()
    # try:
    #    main()
    #except Exception as error:
    #    debug(error)
    main()
