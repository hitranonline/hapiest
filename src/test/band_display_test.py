import math
import sys
import threading
from time import sleep
import sys
import threading
from time import sleep
import random

from test.test import Test
from PyQt5 import QtGui, QtWidgets, QtCore
from widgets.band_display_window_gui import BandDisplayWindowGui
from utils.band import Band, Bands

class BandDisplayTest(Test):
    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'band display test'

    def test(self) -> bool:
        app = QtWidgets.QApplication([])
        window = QtWidgets.QMainWindow()

        def close_window():
            sleep(0.25)
            # window.deleteLater()

        step = 0.1

        random.seed(0xCAFEBABE)
        x = list(map(lambda x: float(x) * step, range(0, int(100.0 / step))))
        def random_band():
            freq = float(random.randint(1, 10)) / 300
            amp = float(random.randint(1, 40))
            y = [0.0] * len(x)
            for i in range(0, int(100.0 / step)):
                y[i] = amp * math.sin(freq * x[i])
            return Band(x, y, "{}, {}".format(freq, amp))

        bands1 = Bands()
        for i in range(0, 100):
            bands1.add_band(random_band())
        bands2 = Bands()
        for i in range(0, 20):
            bands2.add_band(random_band())

        t = threading.Thread(target=close_window)
        t.start()
        widget = BandDisplayWindowGui()
        widget.setMinimumSize(256, 256)
        widget.add_bands(bands1)
        widget.add_bands(bands2)
        window.setCentralWidget(widget)
        window.show()
        return app.exec_() == 0
