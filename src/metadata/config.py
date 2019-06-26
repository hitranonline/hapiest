import os.path

import toml


class Config:
    """
    The configuration class is a singleton class that contains static members for each of the
    possible user
    configurable settings.

    """
    config_options = {  # The number of values to display along the x axis in graphs
        'axisx_ticks':            {
            'default_value': 5,
            'display_name':
                             'X-Axis Ticks',
            'tool_tip':
                             'The number of '
                             'ticks that will '
                             'be displayed '
                             'along the x '
                             'axis.',
            'type':          int
        },

        # The number of values to display along the y axis in graphs
        'axisy_ticks':            {
            'default_value': 5,
            'display_name':
                             'Y-Axis Ticks',
            'tool_tip':
                             'The number of '
                             'ticks that will '
                             'be displayed '
                             'along the y '
                             'axis.',
            'type':          int
        },

        # The folder where data is stored
        'data_folder':            {
            'default_value': 'data', 'display_name': 'Data Folder',
            'tool_tip': 'The path to the folder where data downloaded from HITRAN will be '
                        'stored.', 'type': str
        },

        # Whether the program should be ran with high-dpi scaling enabled.
        'high_dpi':               {
            'default_value': False,
            'display_name': 'High DPI Mode',
            'tool_tip': 'Whether to use high DPI mode or not. If the program looks strange '
                        'on your screen you may want '
                        'to enable this.', 'type': bool
        },

        # The number of rows that tables should be paginated with.
        'select_page_length':     {
            'default_value': 100,
            'display_name':
                             'View Page Length',
            'tool_tip':
                             'The number of '
                             'rows to show '
                             'per page in the '
                             'view table.',
            'type':          int
        },

        'hapi_api_key':           {
            'default_value': '0000', 'display_name': 'HAPI API Key',
            'tool_tip':      'The HAPI API key that is needed to use HAPI v2 functionality.',
            'type':          str
        },
        'axisx_label_format':  {
            'default_value': '%.3E', 'display_name': 'Axis-X Tick Label Format',
            'tool_tip': 'Format specifier for the tick labels. This should be a C-Style '
                        'format.',
            'type': str
        },

        'axisx_log_label_format': {
            'default_value': '%.3E', 'display_name': 'Log Axis-X Tick Label Format',
            'tool_tip': 'Format specifier for the tick labels. This should be a C-Style '
                        'format.', 'type': str
        },

        'axisy_label_format':     {
            'default_value': '%.3E', 'display_name': 'Axis-Y Tick Label Format',
            'tool_tip': 'Format specifier for the tick labels. This should be a C-Style '
                        'format.', 'type': str
        },

        'axisy_log_label_format': {
            'default_value': '%.3E', 'display_name': 'Log Axis-Y Tick Label Format',
            'tool_tip': 'Format specifier for the tick labels. This should be a C-Style '
                        'format.', 'type': str
        },
    }

    DEFAULT_CONFIG = ""

    CONFIG_LOCATION = os.getcwd() + '/Config.toml'

    axisx_ticks = None
    axisy_ticks = None
    data_folder = None
    high_dpi = None
    select_page_length = None
    hapi_api_key = None
    axisx_label_format = None
    axisx_log_label_format = None
    axisy_label_format = None
    axisy_log_label_format = None

    @staticmethod
    def gen_config_string():
        config_string = "[hapiest]\n"

        for name, meta in Config.config_options.items():
            ty = meta['type']
            if ty == str:
                config_string += '{} = \'{}\'\n'.format(name, Config.__dict__[name])
            elif ty in [int, bool, float]:
                config_string += '{} = {}\n'.format(name, str(Config.__dict__[name]).lower())

        return config_string

    @staticmethod
    def config_init():
        """
        Reads in the config file. If it doesn't exist, it will create it with the default settings
        set.
        """
        for name, meta in Config.config_options.items():
            setattr(Config, name,
                    meta['default_value'])  # Config.__dict__[name] = meta['default_value']

        Config.DEFAULT_CONFIG = Config.gen_config_string()

        if not os.path.isfile(Config.CONFIG_LOCATION):
            Config.write_config(Config.DEFAULT_CONFIG)
        else:
            with open(Config.CONFIG_LOCATION, 'r') as file:
                text = file.read()
                Config.load_config(text)

    @staticmethod
    def rewrite_config():
        """
        Generates a new config string, then writes it to the disk.
        """
        Config.write_config(Config.gen_config_string())

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

        :param dict The parsed toml key-value dictionary
        """
        for key, _ in Config.config_options.items():
            if key in dict['hapiest'] and key in Config.config_options and type(
                    dict['hapiest'][key]) == Config.config_options[key]['type']:
                setattr(Config, key, dict['hapiest'][key])

        # Config.data_folder = dict['hapiest']['data_folder']  # Config.high_dpi = dict[
        # 'hapiest']['high_dpi']  # Config.select_page_length = dict['hapiest'][
        # 'select_page_length']  # Config.hapi_api_key = dict['hapiest']['hapi_api_key']

    # Tries to load a configuration, if it fails
    @staticmethod
    def load_config(config_text):
        """
        Attempts to load a configuration from the supplied text. If it fails to do so,
        it sets unspecified values to their defaults.
        
        :param config_text The text of the configuration file
        """
        try:
            parsed = toml.loads(config_text)
            Config.set_values(parsed)
        except Exception as e:
            print(e)


# Statically loads the configuration!
Config.config_init()
