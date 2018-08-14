import os
import re
import sys

from utils.metadata.molecule import MoleculeMeta

if sys.version_info < (3, 6):
    print('You must have Python 3 installed to use hapiest - current version is ' + str(sys.version))
    sys.exit(0)



# If someone launches the program through the command 'python3 __main__.py' this move the working directory to the proper place
srcre = re.compile('.+src\\Z')
if srcre.match(os.getcwd()):
    os.chdir('..')

from windows.main_window import *
from worker.hapi_worker import *
from worker.work_request import *
from worker.hapi_thread import HapiThread
from multiprocessing import freeze_support

if not os.path.exists(Config.data_folder):
    os.makedirs(Config.data_folder)

class App(QtWidgets.QApplication):
    def __init__(self, *args):
        QtWidgets.QApplication.__init__(self, *args)

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


    WorkRequest.start_work_process()

    # Hapi is now started automatically in the work process
    # start = HapiWorker(WorkRequest.START_HAPI, {})
    # start.start() # When a start_hapi request is sent, it starts automatically.

    _ = MoleculeMeta(0)

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
