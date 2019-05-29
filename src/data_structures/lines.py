from typing import *

from metadata.config import *
from worker.hapi_worker import HapiWorker


class Lines:
    """
    An interface for interacting with HITRAN line-by-line data. The data must be in the following
    form:

    ```
    table = {
        'header' : {
            'order' : ('column1','column2','column3'),
            'format' : {
                'column1' : '%10d',
                'column2' : '%20f',
                'column3' : '%30s' 
            },
            'default' : {
                'column1' : 0,
                'column2' : 0.0,
                'column3' : ''
            },
            'number_of_rows' : 3,
            'size_in_bytes' : None,
            'table_name' : 'sampletab',
            'table_type' : 'strict'
        },
        'data' : {
            'column1' : [1,2,3],
            'column2' : [10.5,11.5,12.5],
            'column3' : ['one','two','three']
        }
    }
    ```

    This is the schema hapi version < 2.0 uses already.

    """

    def __init__(self, table: Dict[str, Any]):
        self.table = table
        self.data = table['data']
        self.table_len = len(self.data['nu'])
        self.page_len: int = Config.select_page_length
        self.last_page = int(self.table_len / self.page_len)
        self.last_page_len = self.page_len
        if self.last_page * self.page_len != self.table_len:
            self.last_page_len = self.table_len - self.last_page * self.page_len
            self.last_page += 1

        self.page_number = 1
        self.param_order = table['header']['order']

        self.workers: List['HapiWorker'] = []

        self.param_order = tuple(self.param_order)

    def get_len(self):
        """
        """
        if self.page_number == self.last_page:
            return self.last_page_len
        else:
            return self.page_len

    # Line number is base 0!
    def get_line(self, line_number: int) -> Optional['Line']:
        """
        """
        line = []

        # index of the `line_number`th field of page 
        index = line_number + ((self.page_number - 1) * self.page_len)
        for param in self.param_order:
            line.append(self.data[param][index])
        l = Line(line_number + (self.page_number - 1) * self.page_len, line, self)
        return l

    def set_page(self, page_number):
        self.page_number = page_number


class Line:
    def __init__(self, line_index: int, line: List[Union[int, float, str]], lines: 'Lines'):
        self.line_index = line_index
        self.line = line
        self.lines = lines
        self.data = lines.data
        self.param_order = lines.table['header']['order']

    def update_nth_field(self, field_index: int, new_value: Union[int, float, str]):
        """
        *Given params: (self), int field_index, and a new values : [int,float], updates a field
        for the Line class.*
        """
        self.data[self.param_order[field_index]][self.line_index] = new_value

    def get_nth_field(self, field_index: int) -> Union[int, float]:
        return self.data[self.param_order[field_index]][self.line_index]
