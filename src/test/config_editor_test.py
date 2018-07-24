import math
import threading
from time import sleep
import random

from test.test import Test
from PyQt5 import QtWidgets
from widgets.graphing.band_display_window_gui import BandDisplayWindowGui
from utils.graphing.band import Band, Bands
from utils.metadata.config import *

class ConfigEditorTest(Test):
    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'config editor test'

    def test(self) -> bool:
        app = QtWidgets.QApplication([])
        window = QtWidgets.QMainWindow()
        window.setWindowTitle("Config")

        def close_window():
            sleep(0.25)
            # window.deleteLater()

        t = threading.Thread(target=close_window)
        t.start()
        widget = ConfigEditorWidget()
        widget.setMinimumSize(256, 256)
        window.setCentralWidget(widget)
        window.show()
        return app.exec_() == 0
