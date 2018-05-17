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

        self.table_name = table_name

        self.main_window = parent

        self.next_button = parent.next_button
        self.back_button = parent.back_button
        self.save_button = parent.edit_save_button

        self.next_button.clicked.connect(self.next_page)
        self.back_button.clicked.connect(self.back_page)
        self.save_button.clicked.connect(self.save_table)

        self.last_page = False
        self.current_page = 0
        self.current_page_len = Config.select_page_length
        self.page_len = Config.select_page_length
        self.setRowCount(self.page_len)

        if self.table_name != None:
            self.workers = []
            args = HapiWorker.echo(table_name=table_name, page_len=self.page_len, page_number=self.current_page)

            self.start_worker = HapiWorker(WorkRequest.TABLE_GET_LINES_PAGE, args, self.display_first_page)
            self.start_worker.start()
        else:
            self.workers = []
            self.next_button.setDisabled(True)
            self.back_button.setDisabled(True)
            self.save_button.setDisabled(True)

        self.items = []
        self.double_validator = QDoubleValidator()
        self.double_validator.setNotation(QDoubleValidator.ScientificNotation)
        self.int_validator = QIntValidator()

    def display_first_page(self, work_result: WorkResult):
        """
        *Displays first page of info for edit functionity.*
        """
        lines: Lines = Lines(**work_result.result)
        self.setColumnCount(len(lines.param_order))
        self.setHorizontalHeaderLabels(lines.param_order)
        vertical_labels = map(str, range(0, self.page_len))
        self.setVerticalHeaderLabels(vertical_labels)

        def update_field(column, row, line_edit):
            """
            *Given a column, row, and a line edit, the method alters a field in the data.*
            """
            def f():
                t = type(self.lines.parameters[self.lines.param_order[column]][0])
                value = line_edit.text()
                line = self.lines.get_line(row)
                if t == int:
                    line.update_nth_field(column, int(value))
                elif t == float:
                    line.update_nth_field(column, float(value))
                else:
                    line.update_nth_field(column, value)

            return f


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

                line_edit.editingFinished.connect(update_field(column, row, line_edit))

                self.setCellWidget(row, column, line_edit)
                self.items[row].append(line_edit)
                line_edit.setText(str(item))
        self.display_page(work_result)

    def try_display_page(self, work_result: WorkResult):
        self.display_page(work_result)

    def display_page(self, work_result: WorkResult):
        if not work_result:
            self.last_page = True
            return

        self.next_button.setEnabled(True)
        self.back_button.setEnabled(True)


        result = work_result.result
        self.last_page = result['last_page']
        lines: Lines = Lines(**result)
        self.lines = lines

        self.last_page = lines.last_page
        page_min = result['page_number'] * result['page_len']
        self.setVerticalHeaderLabels(map(str, range(page_min, page_min + self.current_page_len)))
        # for i in range(0, self.current_page_len):
        #    item = self.verticalHeaderItem(i)
        #    item.setText(str(page_min + i))

        for row in range(0, self.current_page_len):
            line = lines.get_line(row)
            for column in range(0, len(lines.param_order)):
                x = line.get_nth_field(column)
                self.items[row][column].setText(str(line.get_nth_field(column)))
        self.main_window.edit_button.setEnabled(True)
        self.save_button.setEnabled(True)

    def remove_worker_by_jid(self, jid: int):
        """
        *Params : int jid (job id), the method terminates a worker thread based on a given job id.*
        """
        for worker in self.workers:
            if worker.job_id == jid:
                worker.safe_exit()
                break

    def next_page(self):
        """
        *Advance the page by one.*
        """
        if self.last_page:
            return

        self.next_button.setDisabled(True)
        self.back_button.setDisabled(True)
        self.save_button.setDisabled(True)

        self.lines.commit_changes()
        self.current_page += 1
        args = HapiWorker.echo(table_name=self.table_name, page_len=self.page_len, page_number=self.current_page)
        worker = HapiWorker(WorkRequest.TABLE_GET_LINES_PAGE, args, self.try_display_page)
        self.workers.append(worker)
        worker.start()


    def back_page(self):
        """
        *Displays previous page, or nothing if already on first page.*
        """
        if self.current_page == 0:
            return
        if self.last_page:
            self.last_page = False

        self.next_button.setDisabled(True)
        self.back_button.setDisabled(True)
        self.save_button.setDisabled(True)


        self.lines.commit_changes()
        self.current_page -= 1

        args = HapiWorker.echo(table_name=self.table_name, page_len=self.page_len, page_number=self.current_page)
        worker = HapiWorker(WorkRequest.TABLE_GET_LINES_PAGE, args, self.try_display_page)
        self.workers.append(worker)
        worker.start()

    def save_table(self):
        """
        *Saves table information to local machine.*
        """
        self.lines.commit_changes()

        self.back_button.setDisabled(True)
        self.next_button.setDisabled(True)

        self.save_button.setDisabled(True)

        worker = HapiWorker(WorkRequest.TABLE_WRITE_TO_DISK,
                            {'source_table': self.table_name, 'output_table': self.main_window.get_edit_output_name()},
                            self.done_saving)
        self.workers.append(worker)
        worker.start()

    def done_saving(self, work_result: WorkResult):
        """
        *handles user feedback for saving of edit tab data.*
        """
        result = work_result.result
        self.save_button.setEnabled(True)
        if result != True:
            err_log("Error saving to disk...")
            return
        self.remove_worker_by_jid(work_result.job_id)

    def close_table(self):
        if self.table_name:
            self.save_table()
