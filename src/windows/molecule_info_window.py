import PyQt5.QtCore
from utils.log import *
from utils.isotopologue import *
from widgets.molecule_info_widget import *
from worker.hapi_worker import *
from worker.work_result import WorkResult
from windows.window import Window

class MoleculeInfoWindow(Window):

    def __init__(self, parent: Window, molecule_name: str):
        """
        Initializes the GUI and sends a work request for the graph to be plotted, and connect 
        signals to the appropriate handler methods.

        @param parent the parent QObject
        @param molecule_name the name of the molecule with no formatting, e.g. H2O for water.

        """
        Window.__init__(self, MoleculeInfoWidget(molecule_name), parent)
        
        self.molecule_name = molecule_name

        self.gui.setWindowTitle(self.molecule_name)

