from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton


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
