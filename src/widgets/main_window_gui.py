from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QScrollArea, QAction, \
    QStatusBar

from widgets.about_widget import AboutWidget
from widgets.graphing.graphing_widget import *
from widgets.molecule_info_widget import MoleculeInfoWidget
from windows.molecule_info_window import MoleculeInfoWindow
from widgets.gui import GUI

from widgets.select_widget import SelectWidget
from widgets.fetch_widget import FetchWidget
from widgets.edit_widget import EditWidget


class MainWindowGui(GUI, QMainWindow):
    """
    The main window contains most of the functionality. This includes the Edit widget, Fetch widget, Select widget, and
    graphing widget.
    """

    def __init__(self, parent):
        """
        Instantiates all of the widgets for each of the individual tabs
        """
        QMainWindow.__init__(self)
        GUI.__init__(self)

        self.setWindowIcon(program_icon())

        self.parent = parent
        self.workers = []

        # Containers
        self.fetch_container: QVBoxLayout = None

        # Elements in 'Molecules' tab
        self.molecule_container: QVBoxLayout = None
        self.molecules_popout_button: QPushButton = None
        self.selected_molecules: QComboBox = None
        self.molecule_info = None

        # Elements in 'Graphing' tab
        self.graphing_tab: QWidget = None
        self.graphing_container: QVBoxLayout = None

        # Other stuff..
        self.config_action: QAction = None
        self.about_hapiest_action: QAction = None
        self.statusbar: QStatusBar = None

        self.config_window = None
        self.about_window = None

        # All of the gui elements get loaded and initialized by loading the ui file
        uic.loadUi('layouts/main_window.ui', self)

        self.config_action.triggered.connect(self.__on_config_action)
        self.about_hapiest_action.triggered.connect(self.__on_about_action)

        self.fetch_widget = FetchWidget(self)
        self.fetch_container.addWidget(self.fetch_widget)

        self.graphing_widget: QWidget = GraphingWidget(self)
        self.graphing_container.addWidget(self.graphing_widget)

        self.populate_table_lists()
        self.populate_molecule_list()

        # Initially display a molecule in the molecule widget
        self.__on_molecules_current_index_changed(0)
        self.molecules_current_molecule.currentIndexChanged.connect(self.__on_molecules_current_index_changed)
        self.molecules_popout_button.clicked.connect(self.__on_molecules_popout_button)

        self.workers = []

        self.status_bar_label: QWidget = QtWidgets.QLabel("Ready")
        self.statusbar.addWidget(self.status_bar_label)

        # Display the GUI since we're done configuring it
        self.show()

    def closeEvent(self, event):
        if self.config_window:
            self.config_window.close()
        if self.about_window:
            self.about_window.close()
        for window in list(GraphDisplayWindow.graph_windows.values()):
            window.close()
        QMainWindow.closeEvent(self, event)

    def remove_worker_by_jid(self, jid: int):
        """
        *Params : int jid (job id), the method terminates a worker thread based on a given job id.*
        """
        for worker in self.workers:
            if worker.job_id == jid:
                worker.safe_exit()
                break

    def __on_config_action(self, *args):
        # if self.config_window:
        #     self.config_window.close()
        self.config_window = ConfigEditorWidget(None)
        self.config_window.show()

    def __on_about_action(self, *args):
        # if self.about_window:
        #     self.about_window.close()
        self.about_window = AboutWidget(None)
        self.about_window.show()

    def __on_molecules_current_index_changed(self, _index):
        if self.molecule_info != None:
            self.molecule_container.removeWidget(self.molecule_info)
        self.molecule_info = MoleculeInfoWidget(self.molecules_current_molecule.currentText())
        self.molecule_container.addWidget(self.molecule_info)

    def __on_molecules_popout_button(self):
        new_window: MoleculeInfoWindow = MoleculeInfoWindow(self.parent, self.molecules_current_molecule.currentText())
        new_window.gui.show()
        self.parent.add_child_window(new_window)

    def populate_molecule_list(self):
        """
        *Extract the name of each molocule that hapi has data on and add it to the molecule list. Also, enable auto-complete for the combobox.*
        """
        # our list of molecule names in the gui
        for molecule_id, _ in Isotopologue.molecules.items():
            if molecule_id >= 1000:
                continue
            molecule = Isotopologue.from_molecule_id(molecule_id)
        self.molecules_current_molecule.addItems(list(set(get_all_json_molecule_names())))

    def populate_table_lists(self, data_names=None):
        """
        *This method initializes the default table values for the fetch tab and the edit tab.*
        """
        if data_names == None:
            data_names = get_all_data_names()

        # self.edit_widget.table_name.clear()
        # self.edit_widget.table_name.addItems(data_names)
        # self.select_widget.table_name.clear()
        # self.select_widget.table_name.addItems(data_names)
        EditWidget.set_table_names(data_names)
        SelectWidget.set_table_names(data_names)

        self.graphing_widget.data_name.clear()
        self.graphing_widget.data_name.addItems(data_names)
