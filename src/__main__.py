import sys
from shutil import copy2
from PyQt4 import QtGui, uic, QtCore, Qt
from hapi import *
from util import *
from main_window import *
from threading import Thread
import matplotlib.pyplot as plt

util_init()
iso_to_html_init()
app = QtGui.QApplication(sys.argv)
window = MainWindow()
init_console_redirect(window, sys.argv)

def start_hapi():
    print 'Proccessing data in data directory'
    window.gui.fetch_button.setEnabled(False)
    db_begin(CONFIG.data_folder)
    window.gui.fetch_button.setEnabled(True)
    print 'Finished processing data in data directory'

try:
    # call db_begin in a daemon thread because it might take a reallyyy long time
    # if someone exits the program, if it weren't a daemon it would continue to
    # execute in the background. The daemon will exit when the main thread does.
    thread = Thread(target = start_hapi, args=())
    thread.daemon = True
    thread.start()
except Exception as e:
    print 'Error initializing hapi database'
    print e


# Exit code
qt_result = app.exec_()


util_close()

sys.exit(qt_result)
