import csv

from utils.config import Config
from utils.isotopologue import *
from utils.log import *


# Hapiest Meta Data class - to be paired with the .data and .header files generated
# with each fetch request.
class HapiMetaData():
    @staticmethod
    def write(data_name, iso_list):
        with open(Config.data_folder + "/" + data_name + ".hmd", "w+") as file:
            last_index = len(iso_list) - 1
            for i in range(0, last_index + 1):
                file.write(str(iso_list[i]))
                if i != last_index:
                    file.write(",")

    def __init__(self, filename):
        debug(filename)
        self.filename = filename

        # A list of the isotopologues that this hmd file has
        self.isos = []
        # A list of the isos as tuples (M, I)
        self.iso_tuples = []

        try:
            with open(Config.data_folder + "/" + self.filename + ".hmd") as file:
                reader = csv.reader(file)
                for row in reader:
                    for item in row:
                        debug('iso=', item)
                        self.isos.append(Isotopologue.from_global_id(int(item)))
        except Exception as e:
            debug(str(e))

        for item in self.isos:
            self.iso_tuples.append((item.molecule_id, item.iso_id))
