import sys
from shutil import copy2
from PyQt4 import QtGui, uic, QtCore, Qt
from hapi import *
from util import *
from main_window import *
import matplotlib.pyplot as plt

util_init()
db_begin('test_data')
app = QtGui.QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec_())
