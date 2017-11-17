import os.path
import toml

CONFIG_LOCATION = 'Config.toml'
DEFAULT_CONFIG = '''[hapi]
data-folder = 'data'
high-dpi = 'false'
select-page-length = 20
'''


class Config():
    data_folder = 'data'
    high_dpi = 'false'
    select_page_length = 20

    @staticmethod
    def config_init():
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

    # Sets all required config values to their defaults
    @staticmethod
    def set_defaults():
        Config.data_folder = 'data'
        Config.high_dpi = 'false'
        Config.select_page_length = 20

    # Sets values from a parsed toml dictionary
    @staticmethod
    def set_values(dict):
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
        try:
            parsed = toml.loads(config_text)
            Config.set_values(parsed)

        except Exception as e:
            print('Encountered error while parsing Config.toml, setting default config options')
            print(e)
            Config.set_defaults()


Config.config_init()
