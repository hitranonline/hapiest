from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, uic

from utils.isotopologue import *
from widgets.edit_widget import EditWidget
from widgets.select_widget import SelectWidget
from worker.hapi_worker import *

class FetchWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent

        self.children = []

        self.data_name: QLineEdit = None
        self.fetch_button: QPushButton = None
        self.list_container: QWidget = None
        self.molecule_id: QComboBox = None
        self.wn_max: QDoubleSpinBox = None
        self.wn_min: QDoubleSpinBox = None
        self.iso_list = None
        self.param_group_list = None 
        self.param_list = None
        self.select_button: QPushButton = None
        self.edit_button: QPushButton = None

        uic.loadUi('layouts/fetch_widget.ui', self)


        self.populate_molecule_list()
        self.populate_parameter_lists()

        # A regular expression that all valid data-names match (strips out characters that arent safe 
        # for paths in windows / unix operating systems)
        re = QtCore.QRegExp('[^<>?\\\\/*\x00-\x1F]*')
        validator = QtGui.QRegExpValidator(re)
        self.data_name.setValidator(validator)

        self.iso_list.itemPressed.connect(self.__iso_list_item_click)
        self.fetch_button.clicked.connect(self.__handle_fetch_clicked)
        self.wn_max.valueChanged.connect(self.__wn_max_change)
        self.wn_min.valueChanged.connect(self.__wn_min_change)
        self.edit_button.clicked.connect(self.__on_edit_clicked)
        self.select_button.clicked.connect(self.__on_select_clicked)

        # Calling this will populate the isotopologue list with isotopologues of
        # whatever the default selected molecule is. This has to be called after
        # the drop-down list is populated so there is something to be selected
        self.__molecule_id_index_changed()

        # Set the molecule_id change method to the one we defined in the class
        self.molecule_id.currentIndexChanged.connect(self.__molecule_id_index_changed)


        QToolTip.setFont(QFont('SansSerif', 10))
        self.param_group_list.setToolTip('Specifies "non-standard" parameter to query.')
        self.param_list.setToolTip('Specifies parameters to query.')
        self.iso_list.setToolTip('Select the molecule isotopologues you wish to query.')
        self.molecule_id.setToolTip('Type in, or use the drop-down menu to select your molecule.')
        self.data_name.setToolTip('Specify local name for fetched data')
        self.wn_min.setToolTip('Specify lower bound wave number to query, must be positive number.\n(default: absolute min for given molecule).')
        self.wn_max.setToolTip('Specify upper bound wave number to query, must be greater than min wave number.\n(default: absolute max for given molecule)')
        self.fetch_button.setToolTip('Fetch data from HITRAN!')



    def populate_parameter_lists(self):
        """
        Populates the parameter lists with all parameters / parameter groups
        that HITRAN has to offer.
        """

        for group in [item for item in sorted(PARAMETER_GROUPS.keys(), key=str.lower) if item[0].isalpha()]:
            item = QtWidgets.QListWidgetItem(group)
            item.setFlags(item.flags() |
                          QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            item.setCheckState(QtCore.Qt.Unchecked)

            self.param_group_list.addItem(item)

        # Add all parameter groups to the parameter groups list.
        for par in sorted(PARLIST_ALL, key=str.lower):
            item = QtWidgets.QListWidgetItem(par)
            item.setFlags(item.flags() |
                          QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            item.setCheckState(QtCore.Qt.Unchecked)

            self.param_list.addItem(item)


    def populate_molecule_list(self):
        """
        Extract the name of each molocule that hapi has data on and add it to the molecule list. Also, enable auto-complete for the combobox.
        """
        # our list of molecule names in the gui
        for molecule_id, _ in Isotopologue.molecules.items():
            if molecule_id >= 1000:
                continue
            molecule = Isotopologue.from_molecule_id(molecule_id)

            self.molecule_id.addItem(molecule.molecule_name)
 

    def fetch_done(self, work_result: WorkResult):
        """
        User feedback for GUI paramter fields of the fetch function in the Main Window.

        :param work_result contains the work result (error or success)
        """
        try:
            self.parent.remove_worker_by_jid(work_result.job_id)
            result = work_result.result
            self.enable_fetch_button()
            if result != None and 'all_tables' in result:
                log("Successfully finished fetch.")
                self.parent.populate_table_lists(result['all_tables'])
                return
            err_log("Failed to fetch...")
            if isinstance(result, List):
                errs = result
            else:
                errs = [result]
            for err in errs:
                # This means the wavenumber range was too small (probably), so
                # we'll tell the user it is too small
                # TODO: Highlight empty elements / invalid elements
                if err.error == FetchErrorKind.FailedToRetreiveData:
                    err_log('The entered wavenumber range is too small, try increasing it')
                # Not much to do in regards to user feedback in this case....
                elif err.error == FetchErrorKind.FailedToOpenThread:
                    err_log('Failed to open thread to make query HITRAN')
                elif err.error == FetchErrorKind.BadConnection:
                    err_log(
                        'Error: Failed to connect to HITRAN. Check your internet connection and try again.')
                elif err.error == FetchErrorKind.BadIsoList:
                    err_log(' Error: You must select at least one isotopologue.')
                elif err.error == FetchErrorKind.EmptyName:
                    pass

        except Exception as e:
            debug(e)

    def disable_fetch_button(self):
        """
        Disable fetch button to disallow user to stack data requests.
        
        """
        self.fetch_button.setDisabled(True)

    def enable_fetch_button(self):
        """
        Re-enables fetch button to allow user to request data.
    
        """
        self.fetch_button.setEnabled(True)


    ###
    # Event Handlers
    ###

    def __iso_list_item_click(self, item):
        """
        Toggle the item that was activated.
        """
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)


    def __wn_max_change(self, value):
        """
        when the wn_max spinbox changes, make sure it's value isn't lower than that of wn_min, and ensure the value isn't
        greater than the maximum.
        """
        max = self.wn_max.maximum()
        if value > max:
            self.wn_min.setValue(max)
            return


    def __wn_min_change(self, value):
        """
        when the wn_min spinbox changes make sure it's value isn't greater than that of wn_max, and make sure it's value
        isn't below the minimum.
        """
        min = self.wn_min.minimum()
        if value < min:
            self.wn_min.setValue(min)


    def __molecule_id_index_changed(self):
        """
        This method repopulates the isotopologue list widget after the molecule
        that is being worked with changes.
        """
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
        """
        Handles fetching of data, checks to make sure that certain things are proper such as min values being smaller than max numbers.
        """
        self.disable_fetch_button()
        molecule = self.get_selected_molecule()

        numax = self.get_wn_max()
        numin = self.get_wn_min()

        if numax < numin:
            self.numax.setValue(numin)
            self.numin.setValue(numax)
            temp = numin
            numin = numax
            numax = temp

        parameter_groups = self.get_selected_param_groups()
        parameters = self.get_selected_params()
        log(str("Sending fetch request..."))
 
        self.disable_fetch_button()
        work = HapiWorker.echo(
            data_name=self.get_data_name(),
            iso_id_list=self.get_selected_isotopologues(),
            numin=numin,
            numax=numax,
            parameter_groups=parameter_groups,
            parameters=parameters)
        self.worker = HapiWorker(WorkRequest.FETCH, work, callback=self.fetch_done)
        self.parent.workers.append(self.worker)
        self.worker.start()

    def eventFilter(self, object: QObject, event: QEvent):
        if event.type() == QEvent.Close:
            self.children.remove(object)
        return False

    def __on_edit_clicked(self, *args):
        new_edit_window = EditWidget()
        new_edit_window.installEventFilter(self)
        self.children.append(new_edit_window)
        new_edit_window.show()

        EditWidget.set_table_names(get_all_data_names())

    def __on_select_clicked(self, *args):
        new_select_window = SelectWidget()
        new_select_window.installEventFilter(self)
        self.children.append(new_select_window)
        new_select_window.show()

        SelectWidget.set_table_names(get_all_data_names())

    ###
    # Getters
    ###

    def get_selected_molecule(self):
        """
        converts the selected molecule to a molecule id.
        """
        return Isotopologue.from_molecule_name(self.molecule_id.currentText())


    def get_selected_isotopologues(self):
        """
        Returns a list containing all of the checked isotopologues.
        """
        selected_isos = []


        for i in range(self.iso_list.count()):
            # get the i'th item from the list
            item = self.iso_list.item(i)

            # Only add checked items
            if item.checkState() == QtCore.Qt.Checked:
                id = item.data(QtCore.Qt.UserRole)
                selected_isos.append(id)

        return selected_isos


    def get_selected_params(self):
        """
        Returns a list containing all of the checked parameters.
        """
        selected_params = []

        # Look at each parameter and add the checked ones to the list
        for i in range(self.param_list.count()):

            item = self.param_list.item(i)

            if item.checkState() == QtCore.Qt.Checked:
                selected_params.append(str(item.text()))

        return selected_params


    def get_selected_param_groups(self):
        """
        Returns a list containing all of the checked groups.
        """
        selected_groups = []

        # Look at each group and add the checked ones to the list
        for i in range(self.param_group_list.count()):

            item = self.param_group_list.item(i)

            if item.checkState() == QtCore.Qt.Checked:
                selected_groups.append(str(item.text()))

        return selected_groups


    def get_data_name(self):
        """
        Returns data name for fetch tab.
        """
        return str(self.data_name.text()).strip()


    def get_wn_max(self):
        """
        Fetches the double value from the QDoubleSpinBox wn_max.
        """
        return self.wn_max.value()


    def get_wn_min(self):
        """
        Fetches the double value from the QDoubleSpinBox wn_min.
        """
        return self.wn_min.value()
