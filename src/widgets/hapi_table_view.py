from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from worker.hapi_worker import *
from worker.work_request import *
from worker.work_result import *
from utils.lines import *
from functools import reduce
import itertools
from utils.hapiest_util import *

class HapiLineEdit(QLineEdit):

    def __init__(self, table, row, col):
        QLineEdit.__init__(self)
        self.row = row
        self.col = col
        self.table = table
        self.editingFinished.connect(self.__editing_finished_handler)
        self.font_metrics = QFontMetrics(self.font())
        
    def __editing_finished_handler(self):
        """
        Alters a field in the corresponding hapi table. Each cell in the table is
        assigned an on edit function that is generataed using this function.
        """
        t = type(self.table.data[self.table.lines.param_order[self.col]][0])
        value = self.text()
        line = self.table.lines.get_line(self.row)
        if t == int:
            line.update_nth_field(self.col, int(value))
        elif t == float:
            line.update_nth_field(self.col, float(value))
        else:
            line.update_nth_field(self.col, value)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            self.clearFocus()
            self.table.keyPressEvent(event)
        else:
            QLineEdit.keyPressEvent(self, event)

    """def sizeHint(self):
        super_sizehint = QLineEdit.sizeHint(self)
        super_sizehint.setWidth(self.font_metrics.width(self.text()))
        return super_sizehint
"""
"""
class HapiTableDelegate(QStyledItemDelegate):
    def __init__(self, table):
        QStyledItemDelegate.__init__(self)
        self.table = table


    def createEditor(self, parent, option, index):
        line_edit = HapiLineEdit(self.table, index.row(), index.col())
        return line_edit
"""
class HapiTableView(QTableView):
    Row = int
    Column = int
    Position = Tuple[Row, Column]

    def __init__(self, parent, table_name):
        super(HapiTableView, self).__init__()

        self.table_name = table_name
        self.table = None

        self.edit_widget = parent

        self.next_button = parent.next_button
        self.back_button = parent.back_button
        self.save_button = parent.save_button

        self.next_button.clicked.connect(self.next_page)
        self.back_button.clicked.connect(self.back_page)
        self.save_button.clicked.connect(self.save_table)

        self.last_page = False
        self.current_page = 1
        self.current_page_len = Config.select_page_length
        self.page_len = int(Config.select_page_length)

        if self.table_name != None:
            self.workers = []
            args = HapiWorker.echo(table_name=table_name)

            self.start_worker = HapiWorker(WorkRequest.GET_TABLE, args, self.display_first_page)
            self.start_worker.start()
        else:
            self.workers = []
            self.next_button.setDisabled(True)
            self.back_button.setDisabled(True)
            self.save_button.setDisabled(True)

        # self.items = []
        self.double_validator = QDoubleValidator()
        self.double_validator.setNotation(QDoubleValidator.ScientificNotation)
        self.int_validator = QIntValidator() 
        # self.horizontalHeader().setStretchLastSection(True)

    def current_row(self):
        return self.currentIndex().row()
    def current_column(self):
        return self.currentIndex().column()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            current_row = self.current_row()
            if current_row < self.page_len:
                self.setCurrentIndex(self.currentIndex().sibling(current_row + 1, self.current_column()))
        elif key == Qt.Key_Tab:
            current_column = self.current_column()
            if current_column < self.nparams:
                self.setCurrentIndex(self.currentIndex().sibling(self.current_row(), current_column + 1))
        else:
            QTableView.keyPressEvent(self, event)
        
        self.widgets[self.current_row()][self.current_column()].setFocus(Qt.TabFocusReason)
    
    def closeEditor(self, editor, hint):
        if hint == QAbstractItemDelegate.EditNextItem and self.currentColumn() == 1:
            hint = QAbstractItemDelegate.EditPreviousItem
        elif hint == QAbstractItemDelegate.EditPreviousItem and self.currentColumn() == 0:
            hint = QAbstractItemDelegate.EditNextItem

        QTableWidget.closeEditor(editor, hint)


    def display_first_page(self, work_result: WorkResult):
        """
        Displays first page of info for edit functionity, sets 'on edit' functions.
        """
        self.table = work_result.result
        self.data = self.table['data']
        lines: Lines = Lines(self.table)
        self.lines = lines
        nparams = len(lines.param_order)
        self.nparams = nparams

        self.table_model = QStandardItemModel(Config.select_page_length, nparams)
        # self.delegate = HapiTableDelegate(self)
        # self.setItemDelegate(self.delegate)
        self.setModel(self.table_model)
        self.table_model.setHorizontalHeaderLabels(lines.param_order)
       
        self.setModel(self.table_model)

        vertical_labels = map(str, range(1, self.page_len + 1))
        
        self.table_model.setVerticalHeaderLabels(vertical_labels)
        
        self.current_page_len = lines.get_len()
        
        self.column_formats = []
        self.column_widths = []
        new_names = []
        for column in range(0, nparams):
            self.column_formats.append(PARAMETER_META[lines.param_order[column]]["default_fmt"])
            column_width = sum(map(int, itertools.filterfalse(lambda x: not x.isdigit(), ["".join(x) for _, x in itertools.groupby(self.column_formats[column], key=str.isdigit)])))    
            if column_width == 0:
                column_width = 16
            self.setColumnWidth(column, column_width)
            self.column_widths.append(column_width)
            new_names.append(("%-" + str(column_width) + "." +  str(column_width + 1) + "s") % lines.param_order[column])
        
        self.table_model.setHorizontalHeaderLabels(new_names)
        self.widgets = [[0] * self.nparams] * self.current_page_len
        for row in range(0, self.current_page_len):
            line = self.lines.get_line(row)
            # self.items.append([])
            for column in range(0, nparams):
                item = line.get_nth_field(column)
                self.widgets[row][column] = HapiLineEdit(self, row, column)
                self.setIndexWidget(self.table_model.createIndex(row, column), self.widgets[row][column])
                line_edit = self.widgets[row][column]
                if type(item) == float:
                    line_edit.setValidator(self.double_validator)
                elif type(item) == int:
                    line_edit.setValidator(self.int_validator)

                str_value = str(item).strip()

                # self.items[row].append(line_edit)
                line_edit.setText(str_value)
                
        # self.resizeColumnsToContents()
        self.display_page(1)


    def display_page(self, page_number: int):
        if page_number < 1:
            page_number = 1
        elif page_number > self.lines.last_page:
            page_number = self.lines.last_page
        self.current_page = page_number

        self.lines.set_page(self.current_page)

        self.next_button.setEnabled(True)
        self.back_button.setEnabled(True)
        page_min = (self.current_page - 1) * self.lines.get_len()
        self.table_model.setVerticalHeaderLabels(map(str, range(page_min + 1,  1 + page_min + self.current_page_len)))
        # for i in range(0, self.current_page_len):
        #    item = self.verticalHeaderItem(i)
        #    item.setText(str(page_min + i))
        
        # self.table_model.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        nparams = self.lines.param_order
        for row in range(0, self.current_page_len):
            line = self.lines.get_line(row)
            for column in range(0, len(nparams)):
                x = line.get_nth_field(column)
                self.widgets[row][column].setText((self.column_formats[column] % line.get_nth_field(column)).strip())
                        # str(line.get_nth_field(column)).strip())
                # self.items[row][column].setText(str(line.get_nth_field(column)).strip())
        
        self.setVisible(False)
        self.resizeColumnsToContents()
        self.setVisible(True)
        
        self.edit_widget.edit_button.setEnabled(True)
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
        self.next_button.setDisabled(True)
        self.back_button.setDisabled(True)
        self.save_button.setDisabled(True)
        self.display_page(self.current_page + 1)

    def back_page(self):
        """
        *Displays previous page, or nothing if already on first page.*
        """
        self.next_button.setDisabled(True)
        self.back_button.setDisabled(True)
        self.save_button.setDisabled(True)
        self.display_page(self.current_page - 1)

    def save_table(self):
        """
        *Saves table information to local machine.*
        """
        self.edit_widget.edit_button.setDisabled(True)
        self.edit_widget.table_name.setDisabled(True)
        self.edit_widget.output_name.setDisabled(True)
        self.edit_widget.next_button.setDisabled(True)
        self.edit_widget.back_button.setDisabled(True)
        self.save_button.setDisabled(True)

        worker = HapiWorker(WorkRequest.SAVE_TABLE,
                            {'table': self.table, 'name': self.edit_widget.get_output_name()},
                            self.done_saving)
        self.workers.append(worker)
        worker.start()

    def done_saving(self, work_result: WorkResult):
        """
        Handles user feedback for saving of edit tab data.
        """
        result = work_result.result
        self.save_button.setEnabled(True)
        if result != True:
            err_log("Error saving to disk...")
            return
        self.remove_worker_by_jid(work_result.job_id)
 
        self.edit_widget.edit_button.setEnabled(True)
        self.edit_widget.table_name.setEnabled(True)
        self.edit_widget.output_name.setEnabled(True)
        self.edit_widget.next_button.setEnabled(True)
        self.edit_widget.back_button.setEnabled(True)
        
        table_lists = get_all_data_names() 
        self.edit_widget.parent.populate_table_lists(table_lists)
        index = table_lists.index(self.edit_widget.get_output_name())
        if index != -1:
            self.edit_widget.table_name.setCurrentIndex(index)


    def close_table(self):
        if self.table_name:
            self.next_page()

