from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from utils.dsl import DSL
from widgets.graphing_widget import *
from utils.log import *
from widgets.hapi_table_view import HapiTableView
from widgets.molecule_info_widget import MoleculeInfoWidget
from windows.molecule_info_window import MoleculeInfoWindow
from widgets.gui import GUI

from widgets.select_widget import SelectWidget
from widgets.fetch_widget import FetchWidget
from widgets.edit_widget import EditWidget

class MainWindowGui(GUI, QMainWindow):
    # Constructor for the gui - essentially just calls the parent constructor
    # and loads the ui layout
    def __init__(self, parent):
        QMainWindow.__init__(self)
        GUI.__init__(self)

        self.parent = parent
        self.workers = []
        
        self.about: QTextEdit = None
    
        # Containers
        self.select_container: QVBoxLayout = None
        self.fetch_container: QVBoxLayout = None
        self.edit_container: QVBoxLayout = None

        # Elements in 'Molecules' tab
        self.molecule_container: QVBoxLayout = None
        self.molecules_popout_button: QPushButton = None
        self.selected_molecules: QComboBox = None
        self.molecule_info = None

        # Elements in 'Graphing' tab
        self.graphing_tab: QWidget = None
        self.graphing_container: QScrollArea = None

        # Other stuff..
        self.graph_window_action: QAction = None
        self.statusbar: QStatusBar = None

        # All of the gui elements get loaded and initialized by loading the ui file
        uic.loadUi('layouts/main_window.ui', self)
        
        self.about.setText(open('res/html/description.html', 'r').read())

        self.fetch_widget = FetchWidget(self)
        self.fetch_container.addWidget(self.fetch_widget)

        self.select_widget = SelectWidget(self)
        self.select_container.addWidget(self.select_widget)
        
        self.edit_widget = EditWidget(self)
        self.edit_container.addWidget(self.edit_widget)
        
        self.populate_table_lists()
        self.populate_molecule_list()
        self.populate_molecule_list()

        self.graphing_widget = GraphingWidget(self)
        self.graphing_container.setWidget(self.graphing_widget)
        # Initially display a molecule in the molecule widget
        self.__on_molecules_current_index_changed(0)
        self.molecules_current_molecule.currentIndexChanged.connect(self.__on_molecules_current_index_changed)
        self.molecules_popout_button.clicked.connect(self.__on_molecules_popout_button)

        self.populate_molecule_list()

        self.workers = []

        self.status_bar_label = QtWidgets.QLabel("Ready")
        self.statusbar.addWidget(self.status_bar_label)
        
        # Display the GUI since we're done configuring it
        self.show()

    def remove_worker_by_jid(self, jid: int):
        """
        *Params : int jid (job id), the method terminates a worker thread based on a given job id.*
        """
        for worker in self.workers:
            if worker.job_id == jid:
                worker.safe_exit()
                break


    def __on_molecules_current_index_changed(self, _index):
        if self.molecule_info != None:
            self.molecule_container.removeWidget(self.molecule_info)
        self.molecule_info = MoleculeInfoWidget(self.molecules_current_molecule.currentText())
        self.molecule_container.addWidget(self.molecule_info)

    def __on_molecules_popout_button(self):
        new_window = MoleculeInfoWindow(self.parent, self.molecules_current_molecule.currentText())
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
            self.molecules_current_molecule.addItem(molecule.molecule_name)
 
    def populate_table_lists(self, data_names=None):
        """
        *This method initializes the default table values for the fetch tab and the edit tab.*
        """
        if data_names == None:
            data_names = get_all_data_names()
        self.edit_widget.table_name.clear()
        self.edit_widget.table_name.addItems(data_names)
        self.select_widget.table_name.clear()
        self.select_widget.table_name.addItems(data_names)
        

