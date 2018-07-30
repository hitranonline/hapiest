from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton

from utils.isotopologue import Isotopologue


class CrossSectionFetchWidget(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)

        self.wn_check: QCheckBox = None
        self.wn_min: QDoubleSpinBox = None
        self.wn_max: QDoubleSpinBox = None

        self.pressure_check: QCheckBox = None
        self.pressure_min: QDoubleSpinBox = None
        self.pressure_max: QDoubleSpinBox = None

        self.temp_check: QCheckBox = None
        self.temp_min: QDoubleSpinBox = None
        self.temp_max: QDoubleSpinBox = None

        self.molecule: QComboBox = None
        self.cross_section: QComboBox = None

        self.fetch_button: QPushButton = None

        uic.loadUi('layouts/cross_section_widget.ui', self)

        for mol_id, molecule_list in Isotopologue.molecules.items():
            molecule = molecule_list[0]
            self.molecule.addItem(molecule.molecule_name)
