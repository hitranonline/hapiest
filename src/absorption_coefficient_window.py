from util import * #edited src.
from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt
from data_handle import * #edited src.
from graph_window import * #edited src.
from hmd import * #edited src.
import threading

class AbsorptionCoefficientWindow():
    graph_type_map = {
        "Voigt": absorptionCoefficient_Voigt,
        "Lorentz": absorptionCoefficient_Lorentz,
        "Gauss": absorptionCoefficient_Gauss,
        "SD Voigt": absorptionCoefficient_SDVoigt,
        "Galatry": absorptionCoefficient_Doppler,
        "HT": absorptionCoefficient_HT
    }
    def __init__(self, parent):
        self.parent = parent
        self.children = []
        self.gui = AbsorptionCoefficientWindowGui()
        self.populate_data_names()
        self.gui.show()

        self.gui.graph_button.clicked.connect(lambda: self.graph())

    def graph(self):
        self.gui.graph_button.setDisabled(True)
        data_name = self.gui.get_data_name()
        hmd = HMD(data_name)
        graph_function = AbsorptionCoefficientWindow.graph_type_map[self.gui.get_graph_type()]

        Components = hmd.iso_tuples[0],
        SourceTables = data_name,
        Environment = {'p': self.gui.get_pressure(), 'T': self.gui.get_temp()}
        GammaL = self.gui.get_broadening_parameter(),
        WavenumberRange = self.gui.get_wn_range(),
        WavenumberStep = self.gui.get_wn_step(),
        WavenumberWing = self.gui.get_wn_wing(),
        WavenumberWingHW = self.gui.get_wn_wing_hw()

        def function(self, errors):
            x, y = graph_function(
                Components=Components,
                SourceTables=SourceTables,
                Environment=Environment,
                GammaL=GammaL[0],
                HITRAN_units=False,
                WavenumberRange=WavenumberRange[0],
                WavenumberStep=WavenumberStep[0],
                WavenumberWing=WavenumberWing[0],
                WavenumberWingHW=WavenumberWingHW
            )
            return (x, y)

        try:
            self.children.append(GraphWindow(lambda errors: function(self, errors)))
        except Exception as e:
            err_(str(e))

    def populate_data_names(self):
        try:
            data_names = DataHandle.get_all_data_names()
            for item in data_names:
                self.gui.data_name.addItem(item)

        except Exception as e:
            err_(e)
            err_("Failed to populate data names...")


class AbsorptionCoefficientWindowGui(QtWidgets.QWidget):
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        uic.loadUi('layouts/absorption_coefficient_window.ui', self)
        self.wn_step_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_step_enabled, self.wn_step))
        self.wn_wing_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_enabled, self.wn_wing))
        self.wn_wing_hw_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_hw_enabled, self.wn_wing_hw))
        self.intensity_threshold_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.intensity_threshold_enabled, self.intensity_threshold))

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
