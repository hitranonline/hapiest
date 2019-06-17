import unittest
import threading
from time import sleep
from PyQt5 import QtWidgets
from widgets.config_editor_widget import ConfigEditorWidget


class TestConfigEditor(unittest.TestCase):
    def test_config_editor(self):

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
        self.assertEqual(app.exec_(), 0)
        # self.assertEqual(0, 0)

if __name__ == '__main__':
    unittest.main()