from util import *
from isotopologue import *
import csv


# Hapiest Meta Data class - to be paired with the .data and .header files generated
# with each fetch request.
class HMD():
    def __init__(self, filename):
        self.filename = filename

        # A list of the isotopologues that this hmd file has
        self.isos = []
        # A list of the isos as tuples (M, I)
        self.iso_tuples = []

        try:
            with open(Config.data_folder + "/" + self.filename + ".hmd") as file:
                reader = csv.reader(file)
                for row in reader:
                    for iso in row:
                        self.isos.append(Isotopologue.from_global_id(int(iso)))
        except Exception as e:
            debug(str(e))

        for item in self.isos:
            self.iso_tuples.append((item.molecule_id, item.iso_id))
