import os.path
import toml

CONFIG_LOCATION = 'Config.toml'
DEFAULT_CONFIG = '''[hapi]
data-folder = 'data'
high-dpi = 'false'
'''

class Configuration(object):

    def __init__(self):
        if not os.path.isfile(CONFIG_LOCATION):
            try:
                fh = open(CONFIG_LOCATION, 'w')
                fh.write(DEFAULT_CONFIG)
                fh.close()
            except Exception as e:
                print str(e)
            finally:
                self.set_defaults()
        else:
            with open(CONFIG_LOCATION, 'r') as file:
                text = file.read()

                self.load_config(text)


    # Sets all required config values to their defaults
    def set_defaults(self):
        self.data_folder = 'data'
        self.high_dpi = 'false'


    # Sets values from a parsed toml dictionary
    def set_values(self, dict):
        self.set_defaults()
        try:
            self.data_folder = dict['hapi']['data-folder']
            self.high_dpi = dict['hapi']['high-dpi']

        except Exception as e:
            print 'Encountered error while initializing program configuration'
            print e


    # Tries to load a configuration, if it fails
    def load_config(self, config_text):
        try:
            parsed = toml.loads(config_text)
            self.set_values(parsed)

        except Exception as e:
            print 'Encountered error while parsing Config.toml, setting default config options'
            print e
            self.set_defaults()
