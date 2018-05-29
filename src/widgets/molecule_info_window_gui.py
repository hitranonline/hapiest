from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt
from utils.hapiest_util import *
from PyQt5.QtChart import *
from utils.log import *
from utils.isotopologue import Isotopologue
from widgets.gui import GUI

class MoleculeInfoWindowGui(GUI, QtWidgets.QWidget):
    def __init__(self, iso: Isotopologue):
        QtWidgets.QWidget.__init__(self)
        GUI.__init__(self)
        
        self.nu_max: QLabel = None
        self.nu_min: QLabel = None
        self.weight: QLabel = None
        self.mol_id: QLabel = None
        self.iso_id: QLabel = None
        self.chemical_formula: QLabel = None
        self.abundance: QLabel = None
        self.image_area: QWidget = None

        uic.loadUi('layouts/molecule_info_window.ui', self)

        self.iso = iso
        print('Remove the if False line in MoleculeInfoWindowGui if Isotopologue has been updated')
        if False:
            self.image_area.setStyleSheet("background-image: url('img/{}.png');".format(iso.iso_name))
            self.abundance.setText(str(iso.abundance))
            self.nu_min.setText(str(iso.nu_min))
            self.nu_max.setText(str(iso.nu_max))
            self.mol_id.setText(str(iso.mol_id))
            self.iso_id.setText(str(iso.iso_id))
            self.chemical_formula.setRichText(iso.html)
            self.weight.setText(str(iso.weight))
