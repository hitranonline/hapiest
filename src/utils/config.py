import os.path
import toml
import sys

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
    select_page_length = 100

    DEFAULT_CONFIG =  """[hapiest]
data_folder = '{data_folder}'
high_dpi = '{high_dpi}'
select_page_length = {select_page_length}
hapi_api_key = '{hapi_api_key}'
""".format(
        data_folder = data_folder,
        high_dpi = high_dpi,
        select_page_length = select_page_length,
        hapi_api_key = 'default')
    
    CONFIG_LOCATION = 'Config.toml'
   
    @staticmethod
    def config_init():
        """
        Reads in the config file. If it doesn't eist, it will create it with the default settings set.
    
        """

        if not os.path.isfile(Config.CONFIG_LOCATION):
            try:
                fh = open(Config.CONFIG_LOCATION, 'w')
                fh.write(Config.DEFAULT_CONFIG)
                fh.close()
            except Exception as e:
                print("Encountered error while attempting to read configuration file: " + str(e))
            finally:
                Config.set_defaults(Config.__dict__)
        else:
            with open(Config.CONFIG_LOCATION, 'r') as file:
                text = file.read()

                Config.load_config(text)


    @staticmethod
    def set_defaults(dict):
        """
        Sets default values.
        
        """
        def set_if_none(name, default_value):
            if name not in dict['hapiest']:
                dict['hapiest'][name] = default_value
        set_if_none('hapi_api_key', '') 
        set_if_none('data_folder', 'data')
        set_if_none('high_dpi', Config.high_dpi)
        set_if_none('select_page_length', Config.select_page_length)

    @staticmethod
    def set_values(dict):
        """
        Sets values from a parsed toml dictionary.

        @param dict The parsed toml key-value dictionary
        
        """
        Config.set_defaults(dict)
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
            print('Encountered error while parsing Config.toml, setting default config options')
            print(e)
            dict = { 'hapiest': {} }
            Config.set_defaults(dict)
            Config.set_values(dict)

# Statically loads the configuration!
Config.config_init()
