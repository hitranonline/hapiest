import sys
import threading
from time import sleep
import sys
import threading
from time import sleep

from test.test import Test
from PyQt5 import QtGui, QtWidgets, QtCore
from widgets.band_display_window_gui import BandDisplayWindowGui
from utils.band import Band, Bands

band = Bands([Band([0, 1, 2, 3], [3, 2, 1, 0], "a"),
              Band([0, 1, 2, 3], [0, 1, 2, 3], "b"),
              Band([4, 5, 6, 7], [1, 2, 3, 1], "c"),
              Band([4, 5, 6, 7], [4, 3, 2, 3], "d")], 'test-table')

class BandDisplayTest(Test):
    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'molecule view test'

    def test(self) -> bool:
        app = QtWidgets.QApplication(sys.argv)

        window = QtWidgets.QMainWindow()
        def close_window():
            sleep(0.25)
            # window.deleteLater()

        t = threading.Thread(target=close_window)
        t.start()
        widget = BandDisplayWindowGui()
        widget.add_bands(band)
        window.setCentralWidget(widget)
        window.show()
        qt_result = app.exec_()
        return qt_result == 0
