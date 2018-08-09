from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtWidgets import *

from utils.dsl import DSL
from utils.hapiest_util import program_icon
from utils.log import err_log, debug, log
from worker.hapi_worker import HapiWorker
from worker.work_request import WorkRequest


class SelectWidget(QWidget):

    instances = []

    @staticmethod
    def set_table_names(table_names):
        for widget in SelectWidget.instances:
            widget.table_name.clear()
            widget.table_name.addItems(table_names)

    def __init__(self, parent = None):
        QWidget.__init__(self)
        self.parent = parent


        self.export_button: QPushButton = None
        self.output_name: QLineEdit = None
        self.run_button: QPushButton = None
        self.select_expression: QTextEdit = None
        self.parameter_list: QListWidget = None
        self.table_name: QComboBox = None
        self.select_all_button: QPushButton = None
        self.deselect_all_button: QPushButton = None

        uic.loadUi('layouts/select_widget.ui', self)

        self.setWindowIcon(program_icon())

        self.setWindowTitle("Select")

        self.select_all_button.clicked.connect(self.__on_select_all_button_click)
        self.run_button.clicked.connect(self.__on_run_button_click)
        self.deselect_all_button.clicked.connect(self.__on_deselect_all_button_click)
        
        self.output_name.textChanged.connect(self.__on_output_name_change)
        self.select_expression.textChanged.connect(self.__on_conditions_finished_editing)
        self.select_expression.textChanged.connect(self.__on_conditions_finished_editing)
        
        self.table_name.currentTextChanged.connect(self.__on_select_table_name_selection_changed)

        self.instances.append(self)
       
        self.table_name.setToolTip("Select data table you wish to augment.")
        self.parameter_list.setToolTip("Select the parameters for the select function.")
        self.export_button.setToolTip("Export data into desired format.")


    ###
    # Event Handlers
    ###

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.close()
        self.instances.remove(self)
        QWidget.closeEvent(self, a0)

    def __on_select_all_button_click(self):
        for i in range(0, self.parameter_list.count()):
            self.parameter_list.item(i).setCheckState(QtCore.Qt.Checked)


    def __on_deselect_all_button_click(self):
        for i in range(0, self.parameter_list.count()):
            self.parameter_list.item(i).setCheckState(QtCore.Qt.Unchecked)

    def __on_select_table_name_selection_changed(self, new_selection):
        """
        When the table that is being worked with changes, update the parameter list.
        """
        self.run_button.setDisabled(True)
        if new_selection == '':
            return

        args = HapiWorker.echo(table_name=new_selection)

        worker = HapiWorker(WorkRequest.TABLE_META_DATA, args, self.__on_select_table_name_complete)
        worker.start()
        self.parent.workers.append(worker)


    def __on_select_table_name_complete(self, work_result):
        """
        Removes worker thread, returns results or handles error if no result is returned.
        """
        self.parent.remove_worker_by_jid(work_result.job_id)

        result = work_result.result
        if not result:
            err_log("Something went wrong while requesting meta-data on a table...")
            return

        parameters = result['parameters']
        self.parameter_list.clear()
        for par in parameters:
            item = QtWidgets.QListWidgetItem(par)
            item.setFlags(item.flags() |
                          QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            item.setCheckState(QtCore.Qt.Unchecked)
            self.parameter_list.addItem(item)

        self.run_button.setEnabled(True)

        # Check for errors..
        self.__on_output_name_change()


    def __on_run_button_click(self):
        """
        Creates a HapiWorker to run the Select query.
        """
        selected_params = self.get_select_parameters()
        table_name = self.get_select_table_name()
        new_table_name = self.get_output_table_name()
        expression = self.get_select_expression()
        parsed_expression = DSL.parse_expression(expression)

        if parsed_expression == None and expression.strip() != '':
            err_log('Invalid select expression.')
            return
        if table_name == new_table_name:
            err_log('Cannot have select output table be the same as the input table')
            return

        self.run_button.setDisabled(True)

        args = HapiWorker.echo(ParameterNames=selected_params, TableName=table_name,
                               DestinationTableName=new_table_name, Conditions=parsed_expression)

        worker = HapiWorker(WorkRequest.SELECT, args, self.__on_run_done)
        self.parent.workers.append(worker)
        worker.start()

    def __on_run_done(self, work_result):
        """
        Handles user feedback on success or failure of select function.
        """
        self.run_button.setEnabled(True)
        self.parent.remove_worker_by_jid(work_result.job_id)
        result = work_result.result
        if not result:
            err_log('Error running select..')
            return
        try:
            if 'all_tables' in result:
                all_tables = result['all_tables']
                self.parent.populate_table_lists(all_tables)
            else:
                text = 'Error running select: \'' + str(result) + '\''
                err_log(text)

            # if self.table:
            #     self.table.close_table()
            #     self.table.close()
            #     QWidget().setLayout(self.table_container.layout())
            #
            # self.table = HapiTableView(self, new_table_name)
            # layout = QtWidgets.QGridLayout(self.table_container)
            # layout.addWidget(self.table)
            # self.table_container.setLayout(layout)

            log('Select successfully ran.')
        except Exception as e:
            err_log('Error running select.')
            debug(e)


    def __on_output_name_change(self):
        """
        """
        try:
            output_name = self.output_name.text()
            if output_name.strip() == '':
                self.run_button.setDisabled(True)
                err_log('Select output table cannot be empty')
            else:
                self.run_button.setEnabled(True)

        except Exception as e:
            debug('fug: ' + str(e))


    def __on_conditions_finished_editing(self):
        """
        When the conditions are changed, make sure they are valid - if they're not, disable the install.py button
        and display a warning..
        """
        expression = self.get_select_expression()
        res = DSL.parse_expression(expression)

        if expression.strip() == '':
            self.run_button.setEnabled(True)
        elif res == None:
            self.run_button.setDisabled(True)
        else:
            self.run_button.setEnabled(True)


    ###
    # Getters
    ###

    def get_select_table_name(self):
        """
        Returns the select table name.
        """
        return self.table_name.currentText()


    def get_select_expression(self):
        """
        Returns select expression entered in by user.
        """
        return self.select_expression.toPlainText()


    def get_output_table_name(self):
        """
        Returns the destination table name the user entered for select function.
        """
        return self.output_name.text()


    def get_select_parameters(self):
        """
        Returns the paramaters the user chose for the select function.
        """
        selected = []
        for i in range(self.parameter_list.count()):
            item = self.parameter_list.item(i)

            if item.checkState() == QtCore.Qt.Checked:
                selected.append(item.text())

        return selected
