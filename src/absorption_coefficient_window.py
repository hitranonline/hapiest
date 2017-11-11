import hapiest_util
from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt
from data_handle import *
from graph_window import *
from hmd import *
import worker
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
        try:
            self.populate_data_names()
        except Exception as e:
            print(e)
        self.gui.show()

        def f():
            try:
                self.graph()
            except Exception as e:
                print(str(e))

        self.gui.graph_button.clicked.connect(lambda: f())

    def graph(self):
        self.gui.graph_button.setDisabled(True)
        data_name = self.gui.get_data_name()
        hmd = HMD(data_name)

        Components = hmd.iso_tuples
        SourceTables = data_name
        Environment = {'p': self.gui.get_pressure(), 'T': self.gui.get_temp()}
        GammaL = self.gui.get_broadening_parameter()
        WavenumberRange = self.gui.get_wn_range()
        WavenumberStep = self.gui.get_wn_step()
        WavenumberWing = self.gui.get_wn_wing()
        WavenumberWingHW = self.gui.get_wn_wing_hw()
        graph_fn = self.gui.get_graph_type()

        work = worker.HapiWorker.echo(
            type=worker.Work.ABSORPTION_COEFFICIENT,
            graph_fn=graph_fn,
            Components=Components,
            SourceTables=SourceTables,
            Environment=Environment,
            GammaL=GammaL,
            HITRAN_units=False,
            WavenumberRange=WavenumberRange,
            WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing,
            WavenumberWingHW=WavenumberWingHW,
            title="Absorption Coefficient",
            titlex="wavenumber",
            titley="coef"
        )

        try:
            self.children.append(GraphWindow(work, self))
        except Exception as e:
            hapiest_util.err_log(str(e))

    def populate_data_names(self):
        try:
            data_names = hapiest_util.get_all_data_names()
            for item in data_names:
                self.gui.data_name.addItem(item)

        except Exception as e:
            hapiest_util.debug(str(e))
            hapiest_util.err_log(str(e))
            hapiest_util.err_log("Failed to populate data names...")

    def done_graphing(self):
        self.gui.graph_button.setEnabled(True)


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
