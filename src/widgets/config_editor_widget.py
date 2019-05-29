from PyQt5.QtWidgets import QCheckBox, QDoubleSpinBox, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, \
    QSpinBox, QVBoxLayout, QWidget

from metadata.config import Config


class ConfigEditorWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.setWindowTitle("Config editor")

        self.main_layout = QVBoxLayout()

        from utils.hapiest_util import program_icon

        self.setWindowIcon(program_icon())

        for key, meta in Config.config_options.items():
            layout = QHBoxLayout()
            label = QLabel(meta['display_name'])
            label.setToolTip(meta['tool_tip'])

            layout.addWidget(label)

            ty = meta['type']
            input = None
            if ty == str:
                input = QLineEdit()
                input.setText(Config.__dict__[key])
            elif ty == int:
                input = QSpinBox()
                input.setMaximum(10000000)
                input.setMinimum(-10000000)
                input.setValue(Config.__dict__[key])
            elif ty == float:
                input = QDoubleSpinBox()
                input.setMaximum(1000000000.0)
                input.setMinimum(-1000000000.0)
                input.setValue(Config.__dict__[key])
            elif ty == bool:
                input = QCheckBox()
                input.setChecked(Config.__dict__[key])

            input.setToolTip(meta['tool_tip'])
            layout.addWidget(input)
            setattr(self, key, { 'input': input, 'layout': layout })
            # self.__dict__[key] = {
            #     'input': input,
            #     'layout': layout
            # }

            self.main_layout.addLayout(layout)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.__on_save_clicked)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.__on_cancel_clicked)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.save_button)

        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)

    def __on_save_clicked(self, *_args):
        for key, meta in Config.config_options.items():
            ty = meta['type']
            if ty == str:
                value = self.__dict__[key]['input'].text()
            elif ty in [int, float]:
                value = self.__dict__[key]['input'].value()
            elif ty == bool:
                value = self.__dict__[key]['input'].isChecked()
            else:
                value = None
            setattr(Config, key, value)
            # Config.__dict__[key] = value

        Config.write_config(Config.gen_config_string())
        self.close()

    def __on_cancel_clicked(self, *_args):
        self.close()
