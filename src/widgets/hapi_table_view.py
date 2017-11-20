from PyQt5.QtWidgets import QTableWidget, QLineEdit
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from worker.hapi_worker import *
from worker.work_request import *
from worker.work_result import *
from utils.lines import *
from functools import reduce

class HapiTableView(QTableWidget):
    Row = int
    Column = int
    Position = Tuple[Row, Column]

    def __init__(self, parent, table_name):
        super(HapiTableView, self).__init__()

        self.next_button = parent.next_button
        self.back_button = parent.back_button
        self.save_button = parent.save_button

        self.next_button.clicked.connect(self.next_page)
        self.back_button.clicked.connect(self.back_page)
        self.save_button.clicked.connect(self.save_table)

        self.last_page = False
        self.current_page = 0
        self.current_page_len = Config.select_page_length
        self.page_len = Config.select_page_length
        self.setRowCount(self.page_len)

        self.workers = []

        args = HapiWorker.echo(table_name=table_name, page_len=self.page_len, page_number=self.current_page)

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

                def update_field():
                    t = type(self.lines.parameters[self.lines.param_order[column]][0])
                    value = line_edit.getText()
                    line = self.lines.get_line(row)
                    if t == int:
                        line.update_nth_field(column, int(value))
                    elif t == float:
                        line.update_nth_field(column, float(value))
                    else:
                        line.update_nth_field(column, value)

                # line_edit.editingFinished.connect(update_field)

                self.setCellWidget(row, column, line_edit)
                self.items[row].append(line_edit)
                line_edit.setText(str(item))

        self.display_page(work_result)

    def display_page(self, work_result: WorkResult):
        lines: Lines = work_result.result
        self.lines = lines

        self.last_page = lines.last_page

        for row in range(0, self.page_len):
            line = lines.get_line(row)
            for column in range(0, len(lines.param_order)):
                x = line.get_nth_field(column)
                debug(type(x), x)
                self.items[row][column].setText(str(line.get_nth_field(column)))

    def next_page(self):
        if self.last_page:
            return
        self.lines.commit_changes()
        self.current_page += 1

        args = HapiWorker.echo(table_name=self.table_name, page_len=self.page_len, page_number=self.current_page)
        worker = HapiWorker(WorkRequest.TABLE_GET_LINES_PAGE, args, self.display_page)
        self.workers.append(worker)
        worker.start()

    def back_page(self):
        if self.current_page == 0:
            return

        self.lines.commit_changes()
        self.current_page -= 1

        args = HapiWorker.echo(table_name=self.table_name, page_len=self.page_len, page_number=self.current_page)
        worker = HapiWorker(WorkRequest.TABLE_GET_LINES_PAGE, args, self.display_page)
        self.workers.append(worker)
        worker.start()

    def save_table(self):
        self.lines.commit_changes()

        args = HapiWorker.echo(table_name=self.table_name)
        self.start_worker
