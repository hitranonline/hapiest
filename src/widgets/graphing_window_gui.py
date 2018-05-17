from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtGui import QFont
from utils.hapi_metadata import *
from worker.hapi_worker import HapiWorker
from worker.work_request import WorkRequest
from widgets.gui import GUI

class GraphingWindowGui(GUI, QtWidgets.QWidget):
    def __init__(self):
        GUI.__init__(self)
        QtWidgets.QWidget.__init__(self)

        self.workers = []

        self.data_name_error: QLabel = None
        self.data_name: QComboBox = None
        self.wn_step: QDoubleSpinBox = None
        self.wn_step_enabled: QCheckBox = None
        self.wn_wing: QDoubleSpinBox = None
        self.wn_wing_enabled: QCheckBox = None
        self.wn_wing_hw: QDoubleSpinBox = None
        self.wn_wing_hw_enabled: QCheckBox = None
        self.intensity_threshold: QDoubleSpinBox = None
        self.intensity_threshold_enabled: QCheckBox = None
        self.wn_max: QDoubleSpinBox = None
        self.wn_min: QDoubleSpinBox = None
        self.broadening_parameter: QComboBox = None
        self.data_name: QComboBox = None
        self.graph_button: QPushButton = None
        self.graph_type: QComboBox = None
        self.output_file_format: QLineEdit = None
        self.output_filename: QLineEdit = None
        self.pressure: QDoubleSpinBox = None
        self.temperature: QDoubleSpinBox = None

        # Absorption spectrum tab elements
        self.as_path_length: QDoubleSpinBox = None
        self.as_instrumental_fn: QComboBox = None
        self.graph_as_button: QPushButton = None
        self.as_instrumental_fn_wing: QDoubleSpinBox = None
        self.as_instrumental_resolution: QDoubleSpinBox = None

        # Transmittance spectrum tab elements
        self.ts_path_length: QDoubleSpinBox = None
        self.ts_instrumental_fn: QComboBox = None
        self.graph_ts_button: QPushButton = None
        self.ts_instrumental_fn_wing: QDoubleSpinBox = None
        self.ts_instrumental_resolution: QDoubleSpinBox = None

        # Radiance spectrum tab elements
        self.rs_path_length: QDoubleSpinBox = None
        self.rs_instrumental_fn: QComboBox = None
        self.graph_rs_button: QPushButton = None
        self.rs_instrumental_resolution: QDoubleSpinBox = None
        self.rs_instrumental_fn_wing: QDoubleSpinBox = None


        uic.loadUi('layouts/graphing_window.ui', self)
        self.wn_step_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_step_enabled, self.wn_step))
        self.wn_wing_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_enabled, self.wn_wing))
        self.wn_wing_hw_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_hw_enabled, self.wn_wing_hw))
        self.intensity_threshold_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.intensity_threshold_enabled, self.intensity_threshold))
        self.data_name.currentTextChanged.connect(self.__on_data_name_chagned)
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

        self.adjustSize()


    def __handle_checkbox_toggle(self, checkbox, element):
        """
        *A handler for checkboxes that will either enable or disable the given
        element, depending on whether the checkbox is checked or not.*
        """
        if checkbox.isChecked():
            element.setEnabled(True)
        else:
            element.setDisabled(True)

    def get_broadening_parameter(self):
        """
        *Returns broadening_parameter.*
        """
        return self.broadening_parameter.currentText()

    def get_data_name(self):
        """
        *Returns name of graphing data.*
        """
        return self.data_name.currentText()

    def get_graph_type(self):
        """
        *Returns graph type.*
        """
        return self.graph_type.currentText()

    def get_intensity_threshold(self):
        """
        *Returns Intensity threshold for graph.*
        """
        if self.intensity_threshold_enabled.checkState() == QtCore.Qt.Checked:
            return self.intensity_threshold.value()
        else:
            return DefaultIntensityThreshold

    def get_wn_range(self):
        """
        *Returns Wave number range.*
        """
        return (self.wn_min.value(), self.wn_max.value())

    def get_wn_step(self):
        """
        *Returns wave number step.*
        """
        if self.wn_step_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_step.value()
        else:
            return None

    def get_wn_wing(self):
        """
        *Returns wave number wing.*
        """
        if self.wn_wing_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_wing.value()
        else:
            return None

    def get_wn_wing_hw(self):
        """
        *Returns wave number half width.*
        """
        if self.wn_wing_hw_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_wing_hw.value()
        else:
            return None

    def get_temp(self):
        """
        *Returns temperature for graph.*
        """
        return self.temperature.value()

    def get_pressure(self):
        """
        *Returns pressure for graph.*
        """
        return self.pressure.value()

    def get_as_instrumental_fn(self):
        """
        *Returns Absorption spectrum graph's instrumental fn.*
        """
        return self.as_instrumental_fn.currentText()

    def get_ts_instrumental_fn(self):
        """
        *Returns the Transmittance spectrum graph's instrumental fn.*
        """
        return self.ts_instrumental_fn.currentText()

    def get_rs_instrumental_fn(self):
        """
        *Returns the Radiance spectrum instrumental fn.*
        """
        return self.rs_instrumental_fn.currentText()

    def get_rs_path_length(self):
        """
        *Returns the radiance spectrum graph's path length.*
        """
        return self.rs_path_length.value()

    def get_ts_path_length(self):
        """
        *Returns the transmittance spectrum graph's path length.*
        """
        return self.ts_path_length.value()

    def get_as_path_length(self):
        """
        *Returns the absorbtion spectrum graph's path length.*
        """
        return self.as_path_length.value()

    def get_as_instrumental_fn_wing(self):
        """
        *Returns the absorbtion spectrum graph's instrumental fn wing.*
        """
        return self.as_instrumental_fn_wing.value()

    def get_as_instrumental_resolution(self):
        """
        *Returns the absorbtion spectrum graph's resolution.*
        """
        return self.as_instrumental_resolution.value()

    def get_ts_instrumental_fn_wing(self):
        """
        *Returns the transmittance spectrum graph's fn wing.*
        """
        return self.ts_instrumental_fn_wing.value()

    def get_ts_instrumental_resolution(self):
        """
        *Returns the Transmittance spectrum graph's resolution.*
        """
        return self.ts_instrumental_resolution.value()

    def get_rs_instrumental_fn_wing(self):
        """
        *Returns the radiance spectrum graph's instrumental fn wing.*
        """
        return self.rs_instrumental_fn_wing.value()

    def get_rs_instrumental_resolution(self):
        """
        *Returns the radiance spectrum graph's resolution.*
        """
        return self.rs_instrumental_resolution.value()

    def set_graph_buttons_enabled(self, enabled):
        """
        Enables all graph buttons.
        """
        self.graph_as_button.setEnabled(enabled)
        self.graph_rs_button.setEnabled(enabled)
        self.graph_ts_button.setEnabled(enabled)
        self.graph_button.setEnabled(enabled)

    def remove_worker_by_jid(self, jid: int):
        """
        *Params : int jid (job id), the method terminates a worker thread based on a given job id.*
        """
        for worker in self.workers:
            if worker.job_id == jid:
                worker.safe_exit()
                break

    parameters_required_to_graph = ['molec_id', 'local_iso_id', 'nu', 'sw', 'a', 'elower', 'gamma_air', 'delta_air',
                                    'gamma_self', 'n_air', 'gp', 'gpp']

    def __on_data_name_chagned(self, new_table):
        """
        *Disables all graph buttons. (Inner method callback : enables graph buttons if necessary params to graph are supplied.).*
        """
        self.data_name_error.setText('')
        self.set_graph_buttons_enabled(False)

        def callback(work_result):
            self.remove_worker_by_jid(work_result.job_id)
            result = work_result.result
            if 'parameters' not in result:
                self.set_graph_buttons_enabled(True)
                return
            for param in GraphingWindowGui.parameters_required_to_graph:
                if param not in result['parameters']:
                    self.data_name_error.setText(
                        '<span style="color:#aa0000;">' + 'Table does not have the required parameters!' + '</span>')
                    return
            self.set_graph_buttons_enabled(True)

        worker = HapiWorker(WorkRequest.TABLE_META_DATA, {'table_name': new_table}, callback)
        self.workers.append(worker)
        worker.start()
