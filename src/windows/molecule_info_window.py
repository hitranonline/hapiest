import PyQt5.QtCore
from utils.log import *
from utils.isotopologue import *
from widgets.molecule_info_window_gui import *
from worker.hapi_worker import *
from worker.work_result import WorkResult
from windows.window import Window

class MoleculeInfoWindow(Window):

    def __init__(self, parent: Window, global_id: GlobalIsotopologueId):
        """
        Initializes the GUI and sends a work request for the graph to be plotted, and connect 
		signals to the appropriate handler methods.

        @param parent the parent QObject
        @param global_id the global isotopologue id of the isotopologue that will be the source for
                            displayed info in the window.

        """
        self.iso = Isotopologue.from_global_id(global_id)
        super(MoleculeInfoWindow, self).__init__(MoleculeInfoWindowGui(self.iso), parent)
        
        self.gui.setWindowTitle(self.iso.iso_name)

