from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton
from typing import List

from utils.isotopologue import Isotopologue


class CrossSectionFetchWidget(QWidget):

    ##
    # Constant dictionary that maps HITRAN molecule id to info about that molecule.
    MOLECULES = {}

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
        self.apply_filters: QPushButton = None

        uic.loadUi('layouts/cross_section_widget.ui', self)

        self.pressure_check.toggled.connect(self.gen_toggle_function([self.pressure_max, self.pressure_min]))
        self.temp_check.toggled.connect(self.gen_toggle_function([self.temp_max, self.temp_min]))
        self.wn_check.toggled.connect(self.gen_toggle_function([self.wn_max, self.wn_min]))

        self.pressure_check.setChecked(True)
        self.temp_check.setChecked(True)
        self.wn_check.setChecked(True)

        self.temp_check.toggle()
        self.wn_check.toggle()
        self.pressure_check.toggle()

        for mol_id, molecule_list in Isotopologue.molecules.items():
            molecule = molecule_list[0]
            self.molecule.addItem(molecule.molecule_name)

    def gen_toggle_function(self, other_widgets: List[QWidget]):
        return lambda checked: list(map(lambda widget: widget.setDisabled(not checked), other_widgets))