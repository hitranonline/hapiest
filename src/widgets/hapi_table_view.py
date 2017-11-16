from PyQt5.QtWidgets import QTableWidget


class HapiTableView(QTableWidget):
    def __init__(self, parent, table_name):
        super(HapiTableView, self).__init__()
