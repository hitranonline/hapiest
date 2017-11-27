from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtGui import QFont
from utils.hapi_metadata import *


class GraphingWindowGui(QtWidgets.QWidget):
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        uic.loadUi('layouts/graphing_window.ui', self)
        self.wn_step_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_step_enabled, self.wn_step))
        self.wn_wing_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_enabled, self.wn_wing))
        self.wn_wing_hw_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_hw_enabled, self.wn_wing_hw))
        self.intensity_threshold_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.intensity_threshold_enabled, self.intensity_threshold))
        #TOOLTIPS
        self.data_name.setToolTip("Select the name of the data you wish to graph.")
        self.temperature.setToolTip("Select the temperature to graph the data at.")
        self.pressure.setToolTip("Select the pressure to graph the data at.")
        self.broadening_parameter.setToolTip("Select broadening paramater for data.")
        self.intensity_threshold.setToolTip("Absolute value of minimum intensity.")
        self.wn_min.setToolTip("Select min wavelength for graph.")
        self.wn_max.setToolTip("Select max wavelength for graph.")

        self.wn_step.setToolTip("Select increment for wave number (wn).")
        self.wn_wing.setToolTip("Set distance from the center of each line to the farthest point where the profile is considered to be non zero.")
        self.wn_wing_hw.setToolTip("Set relative value of the line wing in halfwidths")









    # A handler for checkboxes that will either enable or disable the given
    # element, depending on whether the checkbox is checked or not
    def __handle_checkbox_toggle(self, checkbox, element):
        if checkbox.isChecked():
            element.setEnabled(True)
        else:
            element.setDisabled(True)

    def get_broadening_parameter(self):
        return self.broadening_parameter.currentText()

    def get_data_name(self):
        return self.data_name.currentText()

    def get_graph_type(self):
        return self.graph_type.currentText()

    def get_intensity_threshold(self):
        if self.intensity_threshold_enabled.checkState() == QtCore.Qt.Checked:
            return self.intensity_threshold.value()
        else:
            return DefaultIntensityThreshold

    def get_wn_range(self):
        return (self.wn_min.value(), self.wn_max.value())

    def get_wn_step(self):
        if self.wn_step_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_step.value()
        else:
            return None

    def get_wn_wing(self):
        if self.wn_wing_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_wing.value()
        else:
            return None

    def get_wn_wing_hw(self):
        if self.wn_wing_hw_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_wing_hw.value()
        else:
            return None

    def get_temp(self):
        return self.temperature.value()

    def get_pressure(self):
        return self.pressure.value()
