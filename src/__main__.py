import sys
from shutil import copy2
from PyQt5 import QtWidgets, QtCore
from hapi import *              #edited src.
from util import *               #edited src.
from main_window import *        #edited src.
from threading import Thread
from multiprocessing import Process, Value

if Config.high_dpi == 'true':
    # Enable High DPI display with PyQt5
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()

window.gui.adjustSize()
window.gui.setFixedSize(window.gui.size())

init_console_redirect(window, sys.argv)

def start_hapi():
    window.gui.fetch_button.setDisabled(True)
    print('Proccessing data in data directory')
    db_begin(Config.data_folder)
    print('Finished processing data in data directory')
    window.gui.fetch_button.setEnabled(True)
try:
    # call db_begin in a daemon thread because it might take a reallyyy long time
    # if someone exits the program, if it weren't a daemon it would continue to
    # execute in the background. The daemon will exit when the main thread does
    thread = Thread(target = start_hapi, args=())
    thread.daemon = True
    thread.start()
except Exception as e:
    print('Error initializing hapi database')
    print(e)
finally:
    print('\nDone forking hapi initialization thread')

# Exit code
qt_result = app.exec_()


util_close()

sys.exit(qt_result)
