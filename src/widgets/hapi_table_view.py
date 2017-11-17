from PyQt5.QtWidgets import QTableWidget, QLineEdit
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from worker.hapi_worker import *
from worker.work_request import *
from worker.work_result import *
from utils.lines import *
from functools import reduce

class HapiTableView(QTableWidget):
    def __init__(self, parent, table_name):
        super(HapiTableView, self).__init__()

        self.next_button = parent.next_button
        self.back_button = parent.back_button

        self.current_page = 0
        self.current_page_len = Config.select_page_length
        self.page_len = Config.select_page_length
        self.setRowCount(self.page_len)

        args = HapiWorker.echo(table_name=table_name, page_len=20, page_number=0)

        self.start_worker = HapiWorker(WorkRequest.TABLE_GET_LINES_PAGE, args, self.display_first_page)
        self.start_worker.start()
        self.items = []
        self.double_validator = QDoubleValidator()
        self.double_validator.setNotation(QDoubleValidator.ScientificNotation)
        self.int_validator = QIntValidator()

    def display_first_page(self, work_result: WorkResult):
        lines: Lines = work_result.result
        self.setColumnCount(len(lines.param_order))
        self.setHorizontalHeaderLabels(lines.param_order)
        vertical_labels = map(str, range(0, self.page_len))
        self.setVerticalHeaderLabels(vertical_labels)

        self.current_page_len = lines.get_len()
        for row in range(0, self.current_page_len):
            line = lines.get_line(row)
            self.items.append([])
            for column in range(0, len(lines.param_order)):
                item = line.get_nth_field(column)
                line_edit = QLineEdit()
                if type(item) == float:
                    line_edit.setValidator(self.double_validator)
                elif type(item) == int:
                    line_edit.setValidator(self.int_validator)
                self.setCellWidget(row, column, line_edit)
                self.items[row].append(line_edit)
                line_edit.setText(str(item))
        self.display_page(work_result)

    def display_page(self, work_result: WorkResult):
        lines: Lines = work_result.result

        for row in range(0, self.page_len):
            line = lines.get_line(row)
            for column in range(0, len(lines.param_order)):
                x = line.get_nth_field(column)
                debug(type(x), x)
                self.items[row][column].setText(str(line.get_nth_field(column)))
