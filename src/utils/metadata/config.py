import os.path
import toml
import sys

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, \
    QCheckBox


class ConfigEditorWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.setWindowTitle("Config editor")

        self.main_layout = QVBoxLayout()

        for key, meta in Config.config_options.items():
            layout = QHBoxLayout()
            label = QLabel(key)

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
                print(Config.__dict__[key])
                input.setChecked(Config.__dict__[key])

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

    def __on_save_clicked(self, *args):
        for key, meta in Config.config_options:
            ty = meta['type']
            if ty == str:
                value = self.__dict__[key]['input'].currentText()
            elif ty in [int, float]:
                value = self.__dict__[key]['input'].value()
            elif ty == bool:
                value = self.__dict__[key]['input'].isChecked()
            else:
                value = None

            Config.__dict__[key] = value

        Config.write_config(Config.gen_config_string())
        self.close()

    def __on_cancel_clicked(self, *args):
        self.close()

class Config():
    """
    The configuration class is a singleton class that contains static members for each of the possible user
    configurable settings.

    """
    config_options = {
        ## The number of values to display along the x axis in graphs
        'axisx_ticks': {
            'default_value': 5,
            'type': int
        },

        ## The number of values to display along the y axis in graphs
        'axisy_ticks': {
            'default_value': 5,
            'type': int
        },

        ## The folder where data is stored
        'data_folder': {
            'default_value': 'data',
            'type': str
        },

        ## Whether the program should be ran with high-dpi scaling enabled.
        'high_dpi': {
            'default_value': False,
            'type': bool
        },

        ## The number of rows that tables should be paginated with.
        'select_page_length': {
            'default_value': 100,
            'type': int
        },

        'axisx_label_format': {
            'default_value': '%f',
            'type': str
        },

        'axisx_log_label_format': {
            'default_value': '%.3E',
            'type': str
        },

        'axisy_label_format': {
            'default_value': '%f',
            'type': str
        },

        'axisy_log_label_format': {
            'default_value': '%.3E',
            'type': str
        },
    }

    DEFAULT_CONFIG = ""

    CONFIG_LOCATION = 'Config.toml'

    @staticmethod
    def gen_config_string():
        config_string = "[hapiest]\n"

        for name, meta in Config.config_options.items():
            ty = meta['type']
            if ty == str:
                config_string += '{} = \'{}\''.format(name, meta['default_value'])
            elif ty in [int, bool, float]:
                config_string += '{} = {}'.format(name, str(meta['default_value']))

        return config_string

    @staticmethod
    def config_init():
        """
        Reads in the config file. If it doesn't eist, it will create it with the default settings set.
    
        """
        for name, meta in Config.config_options.items():
            if name not in Config.__dict__:
                setattr(Config, name, meta['default_value'])
                # Config.__dict__[name] = meta['default_value']

        Config.DEFAULT_CONFIG = Config.gen_config_string()

        if not os.path.isfile(Config.CONFIG_LOCATION):
            Config.write_config(Config.DEFAULT_CONFIG)
        else:
            with open(Config.CONFIG_LOCATION, 'r') as file:
                text = file.read()
                Config.load_config(text)

    @staticmethod
    def write_config(config_string):
        try:
            fh = open(Config.CONFIG_LOCATION, 'w')
            fh.write(config_string)
            fh.close()
        except Exception as e:
            print("Encountered error while attempting to write configuration file: " + str(e))

    @staticmethod
    def set_values(dict):
        """
        Sets values from a parsed toml dictionary.

        @param dict The parsed toml key-value dictionary
        
        """
        Config.data_folder = dict['hapiest']['data_folder']
        Config.high_dpi = dict['hapiest']['high_dpi']
        Config.select_page_length = dict['hapiest']['select_page_length']
        Config.hapi_api_key = dict['hapiest']['hapi_api_key']
        if Config.hapi_api_key == '':
            print('TODO: Add a link to the registration website and directions on how to add it to Cargo.toml')
            print('If you\'re seeing this, currently, just put anything other than empty string for hapi_api_key in Config.toml and it will work')
            print('The hapi_api_key found in the Config.toml file is invalid or empty.')
            sys.exit(0)

    # Tries to load a configuration, if it fails
    @staticmethod
    def load_config(config_text):
        """
        Attempts to load a configuration from the supplied text. If it fails to do so, it sets unspecified values to
        their defaults.
        
        @param config_text The text of the configuration file
        
        """
        try:
            parsed = toml.loads(config_text)
            Config.set_values(parsed)
        except Exception as e:
            print(e)

# Statically loads the configuration!
Config.config_init()
