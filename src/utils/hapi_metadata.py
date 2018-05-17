import csv

from utils.config import Config
from utils.isotopologue import *
from utils.log import *



class HapiMetaData():
    """
    Hapiest Meta Data class - to be paired with the .data and .header files generated
    with each fetch request.
    
    TODO: Significantly improve and standardize the '.hmd' format.

    """

    @staticmethod
    def write(data_name, iso_list):
        """
        Writes a '.hmd' file.

        @param data_name the name of the data
        @param iso_list a list of all of the isotopologues the data set contains

        """
        with open(Config.data_folder + "/" + data_name + ".hmd", "w+") as file:
            last_index = len(iso_list) - 1
            for i in range(0, last_index + 1):
                file.write(str(iso_list[i]))
                if i != last_index:
                    file.write(",")

    def __init__(self, filename):
        """
        Initializes a '.hmd' by reading it from the supplied filename.
        @param filename the filename to read from
        
        TODO: Generate a '.hmd' file if there is not one present.

        """
        ## The filename
        self.filename = filename

        ## A list of the isotopologues that this hmd file has
        self.isos = []
        ## A list of the isos as tuples (M, I)
        self.iso_tuples = []

        try:
            with open(Config.data_folder + "/" + self.filename + ".hmd") as file:
                reader = csv.reader(file)
                for row in reader:
                    for item in row:
                        self.isos.append(Isotopologue.from_global_id(int(item)))
        except Exception as e:
            debug('Error initializing HapiMetaData object - ', str(e))
        for item in self.isos:
            self.iso_tuples.append((item.molecule_id, item.iso_id))
