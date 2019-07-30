from PyQt5 import uic
from PyQt5.QtWidgets import *
from metadata.config import Config


class ErrorMsgWidget(QWidget):

    def __init__(self, error_string: str):
        QWidget.__init__(self)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QLabel(error_string))
        self.error_string = error_string
        self.show()

    def __continue_offline_clicked(self):
        Config.continue_offline = True
        self.close()
