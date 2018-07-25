from utils.isotopologue import *

class HapiMetaData():
    """
    Hapiest Meta Data class - to be paired with the .data and .header files generated
    with each fetch request.
    """

    HMD_FILEDS = ['numin', 'numax', 'table_name', 'isos']

    def __init__(self, table_name: str, iso_id_list: List[GlobalIsotopologueId] = None, numin: float = None, 
                 numax: float = None):
        self.table_name = table_name
        if iso_id_list == None:
            if not self.initialize_from_file(table_name):
                self.initialize_from_hapi_table(table_name)
                self.save()
        else:
            self.isos = iso_id_list
            self.numin = numin
            self.numax = numax
            self.save()

    def populate_iso_tuples(self):
        self.iso_tuples = list(map(lambda glbl_id: Isotopologue.from_global_id(glbl_id).iso_tuple(), self.isos))

    def initialize_from_file(self, table_name: str):
        """
        Initializes a HapiMetaData object by reading it from the supplied filename.
        :param filename the filename to read from
        """
        try:
            with open(Config.data_folder + "/" + self.table_name + ".hmd", 'r') as file:
                text = file.read()
                self.initialize_from_toml_dict(toml.loads(text))
                return True
        except Exception as e:
            print('Encoutnered error: {}'.format(str(e)))
            print('No HMD file found for table \'{}\'.'.format(self.table_name))
            return False

    def initialize_from_hapi_table(self, table_name):
        if table_name in LOCAL_TABLE_CACHE:
            data = LOCAL_TABLE_CACHE[table_name]['data']
            molec_ids = data['molec_id']
            local_ids = data['local_iso_id']
            nrows = LOCAL_TABLE_CACHE[table_name]['header']['number_of_rows']
            iso_tuples = {}
            for i in range(0, nrows):
                tup = (molec_ids[i], local_ids[i])
                if tup not in iso_tuples:
                    iso_tuples[tup] = None
            
            self.table_name = table_name
            self.iso_tuples = iso_tuples
            self.isos = list(map(lambda tup: Isotopologue.FROM_MOL_ID_ISO_ID[tup].id, iso_tuples))
            self.numin = data['nu'][0] 
            self.numax = data['nu'][nrows - 1]
        else:
            print('Failed to initialize from LOCAL_TABLE_CACHE')

    def initialize_from_toml_dict(self, dict):
        """
        Initializes all of the values in this HapiMetaData object from a dictonary that was read from a toml formatted
        file.
        """
        for field in HapiMetaData.HMD_FILEDS:
            self.__dict__[field] = dict[field]
        self.populate_iso_tuples()


    def as_dict(self):
        dict = {}
        for field in HapiMetaData.HMD_FILEDS:
            dict[field] = self.__dict__[field]
        return dict


    def save(self):
        try:
            with open(Config.data_folder + "/" + self.table_name + ".hmd", "w") as file:
                file.write(toml.dumps(self.as_dict()))
        except Exception as e:
            print('Encountered exeption in HapiMetaData.write: {}'.format(str(e)))

    def save_as(self, new_table_name):
        try:
            with open(Config.data_folder + "/" + new_table_name + ".hmd", "w") as file:
                file.write(toml.dumps(self.as_dict()))
        except Exception as e:
            print('Encountered exeption in HapiMetaData.write: {}'.format(str(e)))
