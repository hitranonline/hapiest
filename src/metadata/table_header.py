import json
from metadata.config import Config

class TableHeader:

    def __init__(self, table_name):
        self.table_name = table_name
        self.populated = False

        try:
            with open(f"{Config.data_folder}/{table_name}.header", "r") as file:
                file_contents = file.read()
            parsed = json.loads(file_contents)
            self.format = parsed['format']
            self.default = parsed['default']
            self.order = parsed['order']
            self.extra = parsed['extra']
            self.extra_format = parsed['extra_format']
            self.populated = True
        except IOError as e:
            print(f"Encountered io error: {str(e)}")
        except Exception as e:
            print(f"Encountered error: {str(e)}")
