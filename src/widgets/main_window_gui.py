from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from utils.fetch_handler import *
from utils.dsl import DSL
from windows.graphing_window import *
from utils.log import *
from widgets.hapi_table_view import HapiTableView


class MainWindowGui(QtWidgets.QMainWindow):
    # Constructor for the gui - essentially just calls the parent constructor
    # and loads the ui layout
    def __init__(self, window):
        super(MainWindowGui, self).__init__()
        self.parent: 'MainWindow' = window

        # Most of the elements that are in the 'Fetch' tab
        self.data_name: QLineEdit = None
        self.err_bad_connection: QLabel = None
        self.err_bad_iso_list: QLabel = None
        self.err_empty_name: QLabel = None
        self.err_small_range: QLabel = None
        self.fetch_button: QPushButton = None
        self.list_container: QWidget = None
        self.molecule_id: QComboBox = None
        self.wn_max: QDoubleSpinBox = None
        self.wn_min: QDoubleSpinBox = None

        # Most of the elements that are in the 'Select' tab
        self.back_button: QToolButton = None
        self.next_button: QToolButton = None
        self.edit_button: QPushButton = None
        self.select_error_container: QWidget = None
        self.export_button: QPushButton = None
        self.output_name: QLineEdit = None
        self.run_button: QPushButton = None
        self.save_button: QPushButton = None
        self.select_expression: QTextEdit = None
        self.select_error_label: QLabel = None
        self.select_parameter_list: QListWidget = None
        self.table_container: QWidget = None
        self.table_name: QComboBox = None

        # Other stuff..
        self.graph_window_action: QAction = None
        self.statusbar: QStatusBar = None

        # All of the gui elements get loaded and initialized by loading the ui file
        uic.loadUi('layouts/main_window.ui', self)

        self.workers = []

        self.iso_list = QtWidgets.QListWidget(self)
        self.param_group_list = QtWidgets.QListWidget(self)
        self.param_list = QtWidgets.QListWidget(self)

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.addWidget(self.iso_list)
        self.splitter.addWidget(self.param_group_list)
        self.splitter.addWidget(self.param_list)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.splitter)
        self.list_container.setLayout(layout)

        self.status_bar_label = QtWidgets.QLabel("Ready")
        self.statusbar.addWidget(self.status_bar_label)
        self.init_molecule_list()

        self.populate_parameter_lists()

        # Connect menu actions to handling functions
        self.graph_window_action.triggered.connect(self.__open_graph_window)

        # ~TOOLTIPS~
            #Fetch tab
        QToolTip.setFont(QFont('SansSerif', 10))
        self.param_group_list.setToolTip('Specifies "non-standard" parameter to query.')
        self.param_list.setToolTip('Specifies parameters to query.')
        self.iso_list.setToolTip('Select the molecule isotopologues you wish to query.')
        self.molecule_id.setToolTip('Type in, or use the drop-down menu to select your molecule.')
        self.data_name.setToolTip('Specify local name for fetched data')
        self.wn_min.setToolTip('Specify lower bound wave number to query, must be positive number.\n(default: absolute min for given molecule).')
        self.wn_max.setToolTip('Specify upper bound wave number to query, must be greater than min wave number.\n(default: absolute max for given molecule)')
        self.fetch_button.setToolTip('Fetch data from HITRAN!')

            #Select tab
        self.back_button.setToolTip("(Edit) Previous page.")
        self.next_button.setToolTip("(Edit) Next page.")
        self.edit_button.setToolTip("Opens interactable data table.")
        self.export_button.setToolTip("Export data into desired format.")
        self.save_button.setToolTip("Save data table.")
        self.table_name.setToolTip("Select data table you wish to augment.")
        self.select_parameter_list.setToolTip("Select the parameters for select() function.")







        # Hide error messages
        self.err_small_range.hide()
        self.err_bad_connection.hide()
        self.err_bad_iso_list.hide()
        self.err_empty_name.hide()

        # Connect the function to be executed when wn_max's value changes
        self.wn_max.valueChanged.connect(self.__wn_max_change)

        # Connect the function to be executed when wn_min's value changes
        self.wn_min.valueChanged.connect(self.__wn_min_change)

        # Calling this will populate the isotopologue list with isotopologues of
        # whatever the default selected molecule is. This has to be called after
        # the drop-down list is populated so there is something to be selected
        self.__molecule_id_index_changed()

        # Set the molecule_id change method to the one we defined in the class
        self.molecule_id.currentIndexChanged.connect(self.__molecule_id_index_changed)

        # Set the fetch_button onclick method to the one we defined in the class
        self.fetch_button.clicked.connect(self.__handle_fetch_clicked)

        # Set the function for when an item gets clicked to the one defined in the class
        self.iso_list.itemPressed.connect(self.__iso_list_item_click)

        self.output_name.textChanged.connect(self.__on_output_name_change)

        self.run_button.clicked.connect(self.__on_run_button_click)

        self.select_expression.textChanged.connect(self.__on_conditions_finished_editing)

        self.table_name.currentTextChanged.connect(self.__on_select_table_name_selection_changed)

        self.edit_button.clicked.connect(self.__on_edit_button_click)

        # A regular expression that all valid data-names match (strips out characters that arent safe for paths in
        # windows / unix operating systems)
        re = QtCore.QRegExp('[^<>?\\\\/*\x00-\x1F]*')
        validator = QtGui.QRegExpValidator(re)
        self.data_name.setValidator(validator)
        # Uncomment this if you'd like to see how HapiTableView looks
        # self.table = HapiTableView(self, 'default_name')
        # layout = QtWidgets.QGridLayout(self.table_container)
        # layout.addWidget(self.table, 0, 0)
        # self.table_container.setLayout(layout)
        # self.statusbar.setParent(self)

        self.populate_select_table_list()

        self.table = None

        # Display the GUI since we're done configuring it
        self.show()

    ###########################################################################
    # Initialization Methods
    ###########################################################################

    def populate_select_table_list(self):
        data_names = get_all_data_names()
        self.table_name.clear()
        self.table_name.addItems(data_names)

    # Populates the parameter lists with all parameters / parameter groups
    # that HITRAN has to offer.
    def populate_parameter_lists(self):
        # Add all parameter groups to the parameter groups list.
        for (group, _) in PARAMETER_GROUPS.items():
            item = QtWidgets.QListWidgetItem(group)
            item.setFlags(item.flags() |
                          QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            item.setCheckState(QtCore.Qt.Unchecked)

            self.param_group_list.addItem(item)

        # Add all parameter groups to the parameter groups list.
        for par in PARLIST_ALL:
            item = QtWidgets.QListWidgetItem(par)
            item.setFlags(item.flags() |
                          QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            item.setCheckState(QtCore.Qt.Unchecked)

            self.param_list.addItem(item)

    # Extract the name of each molocule that hapi has data on and add it to
    # the molecule list. Also, enable auto-complete for the combobox
    def init_molecule_list(self):
        # our list of molecule names in the gui
        for molecule_id, _ in Isotopologue.molecules.items():
            if molecule_id >= 1000:
                continue
            molecule = Isotopologue.from_molecule_id(molecule_id)

            self.molecule_id.addItem(molecule.molecule_name)

        self.molecule_id.setCompleter(None)
        self.molecule_id.setEditable(True)
        self.molecule_id.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

    ###########################################################################
    # Getter methods
    ###########################################################################


    # converts the selected molecule to a molecule id
    def get_selected_molecule(self):
        return Isotopologue.from_molecule_name(self.molecule_id.currentText())

    # Returns a list containing all of the checked isotopologues
    def get_selected_isotopologues(self):
        selected_isos = []

        # Iterate through all of the items in the isotopologue list
        for i in range(self.iso_list.count()):
            # get the i'th item from the list
            item = self.iso_list.item(i)

            # Only add checked items
            if item.checkState() == QtCore.Qt.Checked:
                id = item.data(QtCore.Qt.UserRole)
                selected_isos.append(id)

        return selected_isos

    # Returns a list containing all of the checked parameters
    def get_selected_params(self):
        selected_params = []

        # Look at each parameter and add the checked ones to the list
        for i in range(self.param_list.count()):

            item = self.param_list.item(i)

            if item.checkState() == QtCore.Qt.Checked:
                selected_params.append(str(item.text()))

        return selected_params

    # Returns a list containing all of the checked groups
    def get_selected_param_groups(self):
        selected_groups = []

        # Look at each group and add the checked ones to the list
        for i in range(self.param_group_list.count()):

            item = self.param_group_list.item(i)

            if item.checkState() == QtCore.Qt.Checked:
                selected_groups.append(str(item.text()))

        return selected_groups

    def get_data_name(self):
        return str(self.data_name.text())

    # Fetches the double value from the QDoubleSpinBox wn_max
    def get_wn_max(self):
        return self.wn_max.value()

    # Fetches the double value from the QDoubleSpinBox wn_min
    def get_wn_min(self):
        return self.wn_min.value()

    def get_select_table_name(self):
        return self.table_name.currentText()

    def get_select_expression(self):
        return self.select_expression.toPlainText()

    def get_output_table_name(self):
        return self.output_name.text()

    def get_select_parameters(self):
        selected = []
        for i in range(self.select_parameter_list.count()):
            item = self.select_parameter_list.item(i)

            if item.checkState() == QtCore.Qt.Checked:
                selected.append(item.text())

        return selected

    ###########################################################################
    # Other Stuff
    ###########################################################################

    def remove_worker_by_jid(self, jid: int):
        for worker in self.workers:
            if worker.job_id == jid:
                worker.safe_exit()
                break

    def show_select_error(self, error_message):
        if self.select_error_label == None:
            self.select_error_label: QLabel = QLabel('<span style="color:#aa0000;">' + error_message + '</span>')
            layout = QtWidgets.QGridLayout()
            layout.addWidget(self.select_error_label)
            self.select_error_container.setLayout(layout)
        else:
            self.clear_select_error()
            self.select_error_label.setText('<span style="color:#aa0000;">' + error_message + '</span>')

    def clear_select_error(self):
        if self.select_error_label != None:
            self.select_error_label.setText("")

    def remove_table_view(self):
        if not self.table:
            return

        self.table_container.layout().removeWidget(self.table)


    ###########################################################################
    #  Event Handlers
    ###########################################################################

    def __on_edit_button_click(self):
        try:
            table_name = self.get_select_table_name()
            self.output_name.setText(table_name)

            self.remove_table_view()

            self.table = HapiTableView(self, table_name)
            if self.table_container.layout() == None:
                layout = QtWidgets.QGridLayout(self.table_container)
                layout.addWidget(self.table)
                self.table_container.setLayout(layout)
            else:
                self.table_container.layout().addWidget(self.table)
        except Exception as e:
            debug('edit', e)

    # When the table that is being worked with changes, update the parameter list
    def __on_select_table_name_selection_changed(self, new_selection):
        self.run_button.setDisabled(True)

        args = HapiWorker.echo(table_name=new_selection)
        worker = HapiWorker(WorkRequest.TABLE_META_DATA, args, self.__on_select_table_name_complete)
        worker.start()
        self.workers.append(worker)

    def __on_select_table_name_complete(self, work_result):
        self.remove_worker_by_jid(work_result.job_id)

        result = work_result.result
        if not result:
            err_log("Something went wrong while requesting meta-data on a table...")
            return

        parameters = result['parameters']
        self.select_parameter_list.clear()
        for par in parameters:
            item = QtWidgets.QListWidgetItem(par)
            item.setFlags(item.flags() |
                          QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            item.setCheckState(QtCore.Qt.Unchecked)
            self.select_parameter_list.addItem(item)

        self.run_button.setEnabled(True)

        # Check for errors..
        self.__on_output_name_change()

    # Try to run the select...
    def __on_run_button_click(self):
        self.clear_select_error()

        selected_params = self.get_select_parameters()
        table_name = self.get_select_table_name()
        new_table_name = self.get_output_table_name()
        expression = self.get_select_expression()
        parsed_expression = DSL.parse_expression(expression)

        if parsed_expression == None and expression.strip() != '':
            err_log('Invalid select expression.')
            self.show_select_error('Invalid select expression.')
            return
        if table_name == new_table_name:
            err_log('Cannot have select output table be the same as the input table')
            self.show_select_error('Cannot have select output table be the same as the input table')
            return

        args = HapiWorker.echo(ParameterNames=selected_params, TableName=table_name,
                               DestinationTableName='tmp', Conditions=parsed_expression)

        worker = HapiWorker(WorkRequest.SELECT, args, self.__on_run_done)
        self.workers.append(worker)
        worker.start()

    def __on_run_done(self, work_result):
        self.remove_worker_by_jid(work_result.job_id)
        result = work_result.result
        if not result:
            err_log('Error running select..')
            return
        try:
            new_table_name = result['new_table_name']
            self.remove_table_view()

            self.table = HapiTableView(self, new_table_name)
            if self.table_container.layout() == None:
                layout = QtWidgets.QGridLayout(self.table_container)
                layout.addWidget(self.table)
                self.table_container.setLayout(layout)
            else:
                self.table_container.layout().addWidget(self.table)

            log('Select successfully ran.')
        except Exception as e:
            err_log('Error running select.')
            debug(e)

    # When the output name changes, if it is empty, display a warning and disable the run button - otherwise enable it
    def __on_output_name_change(self):
        try:
            output_name = self.output_name.text()
            if output_name.strip() == '':
                self.run_button.setDisabled(True)
            elif output_name == self.get_select_table_name():
                self.run_button.setDisabled(True)
                err_log('Cannot have select output table be the same as the input table')
                self.show_select_error('Cannot have select output table be the same as the input table')
            else:
                self.run_button.setEnabled(True)
                self.clear_select_error()

        except Exception as e:
            debug(e)

    # When the conditions are changed, make sure they are valid - if they're not, disable the run button
    # and display a warning.
    def __on_conditions_finished_editing(self):
        expression = self.get_select_expression()
        res = DSL.parse_expression(expression)

        if expression.strip() == '':
            self.run_button.setEnabled(True)
        elif res == None:
            self.run_button.setDisabled(True)
        else:
            self.run_button.setEnabled(True)


    # Toggle the item that was activated
    def __iso_list_item_click(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    # when the wn_max spinbox changes, make sure it's value isn't lower than that of wn_min, and ensure the value isn't
    # greater than the maximum.
    def __wn_max_change(self, value):
        max = self.wn_max.maximum()
        if value > max:
            self.wn_min.setValue(max)
            return
        wn_min = self.get_wn_min()
        if value < wn_min:
            self.wn_max.setValue(wn_min + 1.0)

    # when the wn_min spinbox changes make sure it's value isn't greater than that of wn_max, and make sure it's value
    # isn't below the minimum
    def __wn_min_change(self, value):
        min = self.wn_min.minimum()
        if value < min:
            self.wn_min.setValue(min)
            return
        wn_max = self.wn_max.value()
        if value > wn_max:
            self.wn_min.setValue(wn_max - 1.0)

    # This method repopulates the isotopologue list widget after the molecule
    # that is being worked with changes.
    def __molecule_id_index_changed(self):
        molecule = self.get_selected_molecule()

        # Get the range
        min, max = molecule.get_wn_range()

        # Change the range for wn
        self.wn_min.setMinimum(min)
        self.wn_max.setMaximum(max)

        self.wn_min.setValue(min)
        self.wn_max.setValue(max)

        # Remove all old elements
        self.iso_list.clear()

        # For each isotopologue this molecule has..
        for isotopologue in molecule.get_all_isos():

            # Create a new item, ensure it is enabled and can be checked.
            item = QtWidgets.QListWidgetItem()

            # Create a label to allow the rendering of rich text (fancy molecular formulas)
            label = QtWidgets.QLabel(isotopologue.html)

            # Allow the use of html formatted text
            label.setTextFormat(QtCore.Qt.RichText)

            # Make sure there is a key associated with the item so we can use it later
            item.setData(QtCore.Qt.UserRole, isotopologue.id)
            item.setFlags(item.flags() |
                          QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

            # The normal molecule is always at index 1, and we always want that
            # molecule to be selected
            if isotopologue.iso_id != 1:
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)

            self.iso_list.addItem(item)
            self.iso_list.setItemWidget(item, label)

    def __handle_fetch_clicked(self):
        self.parent.disable_fetch_button()
        # Hide any error messages for now, if they persist they'll be shown
        # at the end of the method
        self.err_small_range.hide()
        self.err_bad_connection.hide()
        self.err_bad_iso_list.hide()
        self.err_empty_name.hide()
        molecule = self.get_selected_molecule()

        wn_max = self.get_wn_max()
        wn_min = self.get_wn_min()

        param_groups = self.get_selected_param_groups()
        params = self.get_selected_params()
        log(str("Sending fetch request..."))
        self.fetch_handler = FetchHandler(self.get_data_name(), self.parent, self.get_selected_isotopologues(),
                                          wn_min, wn_max, param_groups, params)

    def __open_graph_window(self):
        try:
            self.parent.child_windows.append(GraphingWindow(self))
        except Exception as e:
            err_log(e)
