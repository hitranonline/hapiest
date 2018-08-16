from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import re

class ApiKeyValidator(QValidator):
    APIKEY_REGEX = re.compile('[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}')

    def __init__(self):
        QValidator.__init__(self)

    def validate(self, string: str, pos: int) -> (QValidator.State, str, int):
        if len(string) == 0:
            return QValidator.Acceptable, string, pos
        ch = string[len(string) - 1]
        if ('a' <= ch <= 'z') or ch == '-' or ('0' <= ch <= '9'):
            return QValidator.Acceptable, string, pos
        else:
            return QValidator.Invalid, string, pos

    def full_key_is_valid(self, string: str) -> bool:
        return ApiKeyValidator.APIKEY_REGEX.match(string) is not None


class ApiKeyHelpWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        self.err = QLabel("")
        self.api_key_area = QLineEdit()
        self.validator: QValidator = ApiKeyValidator()
        self.api_key_area.setValidator(self.validator)
        self.ok_button = QPushButton('Okay')
        self.ok_button.clicked.connect(self.__on_ok_button_clicked)
        layout.addWidget(QLabel("You can find a hapi API key at https://hitran.org.\n"
                                "Paste your API key in the text area below and hit\n"
                                "the 'Ok' button to save it, and then restart the program."))
        layout.addWidget(self.api_key_area)
        layout.addWidget(self.err)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
        self.show()

    def __on_ok_button_clicked(self, _checked):
        if self.validator.full_key_is_valid(self.api_key_area.text()):
            from utils.metadata.config import Config
            Config.hapi_api_key = self.api_key_area.text()
            Config.write_config(Config.gen_config_string())
            self.close()
        else:
            self.err.setText("<b style='color: red'>The key you have entered appears to be invalid.</b>")
