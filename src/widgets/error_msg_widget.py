from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget


class ErrorMsgWidget(QWidget):

    def __init__(self, error_string: str):
        QWidget.__init__(self)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QLabel(error_string))
        self.error_string = error_string
        self.show()
