from util import *
from window import Window
from PyQt5 import QtCore, QtWidgets, QtGui
import re
from data_handle import *
from hapi import *
from absorption_coefficient_window import *
from isotopologue import *
from PyQt5.QtWidgets import (QWidget, QToolTip, QPushButton, QApplication)
from PyQt5.QtGui import QFont

class MainWindow(Window):
    def __init__(self):
        # Initially an empty list, until other windows are created
        self.child_windows = []

        # Create a new instance of the GUI container class
        self.gui = MainWindowGui(self)

        self.is_open = True



    def fetch_error(self, errors):
        if not isinstance(errors, list):
            t = [errors]
            errors = t
        for err in errors:
            # This means the wavenumber range was too small (probably), so
            # we'll tell the user it is too small
            if err.error == FetchErrorKind.FailedToRetreiveData:
                self.gui.err_small_range.show()
                err_(' The entered wavenumber range is too small, try increasing it')
            # Not much to do in regards to user feedback in this case....
            elif err.error == FetchErrorKind.FailedToOpenThread:
                err_(' Failed to open thread to make query HITRAN')
            elif err.error == FetchErrorKind.BadConnection:
                self.gui.err_bad_connection.show()
                err_(' Error: Failed to connect to HITRAN. Check your internet connection and try again.')
            elif err.error == FetchErrorKind.BadIsoList:
                self.gui.err_bad_iso_list.show()
                err_(' Error: You must select at least one isotopologue.')
            elif err.error == FetchErrorKind.EmptyName:
                self.gui.err_empty_name.show()





    def open_graph_window(self):
        # Open a fetch window
        # self.child_windows.append(GraphWindow())
        raise Exception("Unsupported: graph operation")

    def close_window(self, to_close):
        # Close all occurences of the window to_close in the windows list.
        # There should only be one but you never know...
        self.child_windows = filter(
                        lambda window: window != to_close, self.child_windows)
        to_close.close()


    def close(self):
        for window in self.child_windows:
            if window.is_open:
                window.close()

        self.gui.close()


    def open(self):
        self.gui.open()

    # Method that get called when the append_text signal is received by the window
    # This is to allow console output
    def console_append_text(self, text):
        self.gui.console_output.insertPlainText(text)
        self.gui.console_output.moveCursor(QtGui.QTextCursor.End)

    # Method gets called when html formatted text is to be printed to console.
    def console_append_html(self, html):
        self.gui.console_output.insertHtml(html)
        self.gui.console_output.moveCursor(QtGui.QTextCursor.End)


class MainWindowGui(QtWidgets.QMainWindow):
    # Constructor for the gui - essentially just calls the parent constructor
    # and loads the ui layout
    def __init__(self, window):
        super(MainWindowGui, self).__init__()

        self.parent = window

        uic.loadUi('layouts/main_window.ui', self)

        self.init_molecule_list()

        self.populate_parameter_lists()

        # TOOLTIPS
        QToolTip.setFont(QFont('SansSerif', 10))
        self.param_group_list.setToolTip('Specifies "non-standard" parameter to query.')
        self.param_list.setToolTip('Specifies parameters to query.')
        self.iso_list.setToolTip('Select the molecule isotopologues you wish to query.')
        self.molecule_id.setToolTip('Type in, or use the drop-down menu to select your molecule.')
        self.data_name.setToolTip('Specify local name for fetched data')

        self.wn_min.setToolTip('Specify lower bound wave number to query, must be positive number.\n(default: absolute min for given molecule).')
        self.wn_max.setToolTip('Specify upper bound wave number to query, must be greater than min wave number.\n(default: absolute max for given molecule)')
        self.fetch_button.setToolTip('Prompts parameter validation, fetches from HITRAN.')
        self.clear_console.setToolTip('Clear the console of all current output.')
        # Connect menu actions to handling functions
        self.action_absorption_coefficient.triggered.connect(
            lambda: self.__open_absorption_coefficient_window())

        # Hide error messages
        self.err_small_range.hide()
        self.err_bad_connection.hide()
        self.err_bad_iso_list.hide()
        self.err_empty_name.hide()

        # Connect the function to be executed when wn_max's value changes
        self.wn_max.valueChanged.connect(
            lambda value: self.__wn_max_change(value))

        # Connect the function to be executed when wn_min's value changes
        self.wn_min.valueChanged.connect(
            lambda value: self.__wn_min_change(value))

        # Calling this will populate the isotopologue list with isotopologues of
        # whatever the default selected molecule is. This has to be called after
        # the drop-down list is populated so there is something to be selected
        self.__molecule_id_index_changed()

        # Set the molecule_id change method to the one we defined in the class
        self.molecule_id.currentIndexChanged.connect(
            lambda: self.__molecule_id_index_changed())

        # Set the fetch_button onclick method to the one we defined in the class
        self.fetch_button.clicked.connect(
            lambda: self.__handle_fetch_clicked())

        # Set the clear_console button onckick method to the one defined in the class
        self.clear_console.clicked.connect(
            lambda: self.__handle_clear_console_clicked())

        # Set the function for when an item gets clicked to the one defined in the class
        self.iso_list.itemPressed.connect(
            lambda item: self.__iso_list_item_click(item))

        # A regular expression that all valid data-names match (strips out characters that arent safe for paths in
        # windows / unix operating systems)
        re = QtCore.QRegExp('[^<>?\\\\/*\x00-\x1F]*')
        validator = QtGui.QRegExpValidator(re)
        self.data_name.setValidator(validator)

        # Display the GUI since we're done configuring it
        self.show()

    ###########################################################################
    # Initialization Methods
    ###########################################################################

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

    ###########################################################################
    #  Event Handlers
    ###########################################################################


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

    # Clear the console input
    def __handle_clear_console_clicked(self):
        self.console_output.clear()

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
        debug("Hey")
        # Hide any error messages for now, if they persist they'll be shown
        # at the end of the method
        self.err_small_range.hide()
        self.err_bad_connection.hide()
        self.err_bad_iso_list.hide()
        self.err_empty_name.hide()

        molecule = self.get_selected_molecule()

        wn_max = self.get_wn_max()
        wn_min = self.get_wn_min()

        data_handle = DataHandle(self.get_data_name())

        param_groups = self.get_selected_param_groups()
        params = self.get_selected_params()

        result = data_handle.try_fetch(
            self.parent,
            self.get_selected_isotopologues(),
            wn_min,
            wn_max,
            param_groups,
            params)

        if result == True:
            return
        else:
            self.fetch_error(result)

    def __open_absorption_coefficient_window(self):
        try:
            # window = AbsorptionCoefficientWindow(self)
            # Window.start(window)
            self.parent.child_windows.append(AbsorptionCoefficientWindow(self))
        except Exception as e:
            debug(e)
