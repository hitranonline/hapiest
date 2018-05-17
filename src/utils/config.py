import os.path
import toml

CONFIG_LOCATION = 'Config.toml'
DEFAULT_CONFIG = '''[hapi]
data-folder = 'data'
high-dpi = 'false'
select-page-length = 10
'''

class Config():
    """
    The configuration class is a singleton class that contains static members for each of the possible user
    configurable settings.
    """
    
    ## The folder where data is stored
    data_folder = 'data'

    ## Whether the program should be ran with high-dpi scaling enabled.
    high_dpi = 'false'

    ## The number of rows that tables should be paginated with.
    select_page_length = 10

    
    @staticmethod
    def config_init():
        """
        Reads in the config file. If it doesn't eist, it will create it with the default settings set.
        """

        if not os.path.isfile(CONFIG_LOCATION):
            try:
                fh = open(CONFIG_LOCATION, 'w')
                fh.write(DEFAULT_CONFIG)
                fh.close()
            except Exception as e:
                print(str(e))
            finally:
                Config.set_defaults()
        else:
            with open(CONFIG_LOCATION, 'r') as file:
                text = file.read()

                Config.load_config(text)


    @staticmethod
    def set_defaults():
        """
        Sets default values.
        """
        def set_if_none(name, default_value):
            if Config.__dict__[name] == None:
                Config.__dict__[name] = default_value
        
        set_if_none('data_folder', 'data')
        set_if_none('high_dpi', 'false')
        set_if_none('select_page_length', 10)

    @staticmethod
    def set_values(dict):
        """
        Sets values from a parsed toml dictionary.

        Args:
            dict: The parsed toml key-value dictionary.
        """
        Config.set_defaults()
        try:
            Config.data_folder = dict['hapi']['data-folder']
            Config.high_dpi = dict['hapi']['high-dpi']
            Config.select_page_length = dict['hapi']['select-page-length']
        except Exception as e:
            print('Encountered error while initializing program configuration')
            print(e)

    # Tries to load a configuration, if it fails
    @staticmethod
    def load_config(config_text):
        """
        Attempts to load a configuration from the supplied text. If it fails to do so, it sets unspecified values to their defaults.
        
        Args:
            config_text: The text of the configuration file.
        """
        try:
            parsed = toml.loads(config_text)
            Config.set_values(parsed)

        except Exception as e:
            print('Encountered error while parsing Config.toml, setting default config options')
            print(e)
            Config.set_defaults()

# Statically loads the configuration!
Config.config_init()
