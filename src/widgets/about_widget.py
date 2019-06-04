from PyQt5.QtWidgets import QHBoxLayout, QTextEdit, QWidget

from utils.hapiest_util import program_icon


class AboutWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.text = QTextEdit()
        self.text.setText(open('res/html/description.html', 'r').read())
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.text)
        self.setWindowTitle("About hapiest")
        self.setWindowIcon(program_icon())
        self.setMinimumSize(500, 500)
