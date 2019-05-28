import threading
from time import sleep

from PyQt5 import QtWidgets

from test.test import Test
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
            window.deleteLater()

        t = threading.Thread(target=close_window)
        t.start()
        widget = ConfigEditorWidget(None)
        widget.setMinimumSize(256, 256)
        window.setCentralWidget(widget)
        window.show()
        return app.exec_() == 0
