import os
import re

# If someone launches the program through the command 'python3 __main__.py' this move the working directory to the proper place
srcre = re.compile('.+src\\Z')
if srcre.match(os.getcwd()):
    os.chdir('..')

from PyQt5 import QtWidgets, QtCore
from windows.main_window import *
from worker.hapi_worker import *
from utils.console_redirect import *
from utils.log import *
from worker.work_request import *

def main():
    if Config.high_dpi == 'true':
        # Enable High DPI display with PyQt5
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    # Fix for mac-based systems...
    os.environ['no_proxy'] = '*'

    start = HapiWorker(WorkRequest.START_HAPI, {})
    start.start()

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()

    window.gui.adjustSize()
    window.gui.setFixedSize(window.gui.size())

    TextReceiver.init_console_redirect(window, sys.argv)

    WorkRequest.start_work_process()


    qt_result = app.exec_()

    TextReceiver.redirect_close()

    close = HapiWorker(WorkRequest.END_WORK_PROCESS, {}, callback=None)

    WorkRequest.WORKER.process.join()

    sys.exit(qt_result)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        debug(e)
