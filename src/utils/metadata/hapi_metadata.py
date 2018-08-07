from utils.isotopologue import *

class HapiMetaData():
    """
    Hapiest Meta Data class - to be paired with the .data and .header files generated
    with each fetch request.
    """

    HMD_FILEDS = ['numin', 'numax', 'table_name', 'isos', 'dirty_cells']

    def __init__(self, table_name: str, iso_id_list: List[GlobalIsotopologueId] = None, numin: float = None, 
                 numax: float = None, dirty_cells: List[Tuple[int, int]] = []):
        self.table_name = table_name
        self.dirty_cells = set([])
        if iso_id_list == None:
            if not self.initialize_from_file():
                # This should hopefully only be executed in the worker process (since the LOCAL_TABLE_CACHE is not
                # populated in the gui process)
                self.initialize_from_hapi_table(table_name)
                self.save()
        else:
            self.isos = iso_id_list
            self.numin = numin
            self.numax = numax
            self.dirty_cells = set(dirty_cells)
            self.save()

    def add_dirty_cell(self, col, row):
        self.dirty_cells.add((col, row))

    def remove_dirty_cell(self, col, row):
        t = (col, row)
        if t in self.dirty_cells:
            self.dirty_cells.remove(t)

    def populate_iso_tuples(self):
        self.iso_tuples = list(map(lambda glbl_id: Isotopologue.from_global_id(glbl_id).iso_tuple(), self.isos))

    def initialize_from_file(self):
        """
        Initializes a HapiMetaData object by reading it from the supplied filename.
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
            self.dirty_cells = set([])
        else:
            print('Failed to initialize from LOCAL_TABLE_CACHE')

    def initialize_from_toml_dict(self, dict):
        """
        Initializes all of the values in this HapiMetaData object from a dictonary that was read from a toml formatted
        file.
        """
        for field in HapiMetaData.HMD_FILEDS:
            self.__dict__[field] = dict[field]
        if 'dirty_cells' not in self.__dict__:
            self.dirty_cells = set([])
        else:
            self.dirty_cells = set(map(tuple, self.dirty_cells))
        self.populate_iso_tuples()

    def as_dict(self):
        dict = {}
        for field in HapiMetaData.HMD_FILEDS:
            dict[field] = self.__dict__[field]
        return dict

    def save(self):
        self.dirty_cells = list(self.dirty_cells)
        try:
            with open(Config.data_folder + "/" + self.table_name + ".hmd", "w") as file:
                file.write(toml.dumps(self.as_dict()))
        except Exception as e:
            print('Encountered exeption in HapiMetaData.write: {}'.format(str(e)))
        self.dirty_cells = set(self.dirty_cells)

    def save_as(self, new_table_name):
        # Must convert the list of tuples to a list of lists, since the toml library doesn't properly serialize tuples.
        # Must keep them as tuples because lists aren't hashable for some reason.
        self.dirty_cells = list(map(list, self.dirty_cells))
        old_table_name = self.table_name
        self.table_name = new_table_name

        try:
            with open(Config.data_folder + "/" + new_table_name + ".hmd", "w+") as file:
                file.write(toml.dumps(self.as_dict()))
        except Exception as e:
            print('Encountered exeption in HapiMetaData.write: {}'.format(str(e)))

        # Convert back to a list of tuples
        self.dirty_cells = set(map(tuple, self.dirty_cells))
        self.table_name = old_table_name