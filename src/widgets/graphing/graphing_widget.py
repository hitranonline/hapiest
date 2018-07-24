from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QLayout, QComboBox

from utils.log import err_log
from utils.metadata.hapi_metadata import *
from worker.hapi_worker import HapiWorker
from worker.work_request import WorkRequest
from widgets.gui import GUI
from windows.graph_display_window import GraphDisplayWindow
from utils.graphing.graph_type import GraphType
import builtins


class GraphingWidget(GUI, QtWidgets.QWidget):

    ABSORPTION_COEFFICIENT_STRING: str = "Absorption Coefficient"
    ABSORPTION_SPECTRUM_STRING: str = "Absorption Spectrum"
    TRANSMITTANCE_SPECTRUM_STRING: str = "Transmittance Spectrum"
    RADIANCE_SPECTRUM_STRING: str = "Radiance Spectrum"
    BANDS_STRING: str = "Bands"

    str_to_graph_ty = {
        ABSORPTION_COEFFICIENT_STRING: GraphType.ABSORPTION_COEFFICIENT,
        ABSORPTION_SPECTRUM_STRING: GraphType.ABSORPTION_SPECTRUM,
        TRANSMITTANCE_SPECTRUM_STRING: GraphType.TRANSMITTANCE_SPECTRUM,
        RADIANCE_SPECTRUM_STRING: GraphType.RADIANCE_SPECTRUM,
        BANDS_STRING: GraphType.BANDS
    }

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self)
        GUI.__init__(self)

        self.parent = parent

        self.workers = []

        self.line_profile_layout: QLayout = None
        self.wn_layout: QLayout = None
        self.wn_cfg_layout: QLayout = None
        self.plot_title_layout: QLayout = None
        self.graph_button_layout: QLayout = None
        self.window_layout: QLayout = None
        self.data_name_layout: QLayout = None
        self.env_layout: QLayout = None
        self.mixing_ratio_layout: QLayout = None
        self.graph_type_layout: QLayout = None

        self.data_name_error: QLabel = None
        self.data_name: QComboBox = None
        self.use_existing_window: QCheckBox = None
        self.selected_window: QComboBox = None
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
        # Changed to gamma_air, gamma_self proportion
        # self.broadening_parameter: QComboBox = None
        self.gamma_air: QDoubleSpinBox = None
        self.gamma_self: QLabel = None
        self.data_name: QComboBox = None
        self.graph_button: QPushButton = None
        self.line_profile: QComboBox = None
        self.output_file_format: QLineEdit = None
        self.output_filename: QLineEdit = None
        self.pressure: QDoubleSpinBox = None
        self.temperature: QDoubleSpinBox = None

        # Absorption spectrum tab elements
        self.as_path_length: QDoubleSpinBox = None
        self.as_instrumental_fn: QComboBox = None
        self.as_instrumental_fn_wing: QDoubleSpinBox = None
        self.as_instrumental_resolution: QDoubleSpinBox = None

        # Transmittance spectrum tab elements
        self.ts_path_length: QDoubleSpinBox = None
        self.ts_instrumental_fn: QComboBox = None
        self.ts_instrumental_fn_wing: QDoubleSpinBox = None
        self.ts_instrumental_resolution: QDoubleSpinBox = None

        # Radiance spectrum tab elements
        self.rs_path_length: QDoubleSpinBox = None
        self.rs_instrumental_fn: QComboBox = None
        self.rs_instrumental_resolution: QDoubleSpinBox = None
        self.rs_instrumental_fn_wing: QDoubleSpinBox = None

        uic.loadUi('layouts/graphing_widget.ui', self)
        self.wn_step_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_step_enabled, self.wn_step))
        self.wn_wing_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_enabled, self.wn_wing))
        self.wn_wing_hw_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_hw_enabled, self.wn_wing_hw))
        self.intensity_threshold_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.intensity_threshold_enabled, self.intensity_threshold))
        self.use_existing_window.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.use_existing_window, self.selected_window))

        self.graph_button.clicked.connect(self.graph)
        self.graph_type.currentTextChanged.connect(self.__on_graph_type_changed)
        self.data_name.currentTextChanged.connect(self.__on_data_name_chagned)
        self.gamma_air.valueChanged.connect(self.__on_gamma_air_changed)

        # Set initial values automatically for gamma_air and gamma_self
        self.gamma_air.setValue(0.0)
        self.__on_gamma_air_changed(0.0)

        self.update_existing_window_items()
        self.populate_graph_types()
        self.populate_data_names()

        # TOOLTIPS
        self.data_name.setToolTip("Select the name of the data you wish to graph.")
        self.temperature.setToolTip("Select the temperature to graph the data at.")
        self.pressure.setToolTip("Select the pressure to graph the data at.")
        self.intensity_threshold.setToolTip("Absolute value of minimum intensity.")
        self.wn_min.setToolTip("Select min wavelength for graph.")
        self.wn_max.setToolTip("Select max wavelength for graph.")

        self.wn_step.setToolTip("Select increment for wave number (wn).")
        self.wn_wing.setToolTip(
            "Set distance from the center of each line to the farthest point where the profile is considered to be non zero.")
        self.wn_wing_hw.setToolTip("Set relative value of the line wing in halfwidths")

        self.adjustSize()

    def get_standard_parameters(self):
        data_name = self.get_data_name()
        hmd = HapiMetaData(data_name)

        Components = hmd.iso_tuples
        SourceTables = [data_name]
        Environment = {'p': self.get_pressure(), 'T': self.get_temp()}
        Diluent = self.get_diluent()
        WavenumberRange = self.get_wn_range()
        WavenumberStep = self.get_wn_step()
        WavenumberWing = self.get_wn_wing()
        WavenumberWingHW = self.get_wn_wing_hw()
        graph_fn = self.get_line_profile()

        return HapiWorker.echo(
            graph_fn=graph_fn,
            Components=Components,
            SourceTables=SourceTables,
            Environment=Environment,
            Diluent=Diluent,
            HITRAN_units=False,
            WavenumberRange=WavenumberRange,
            WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing,
            WavenumberWingHW=WavenumberWingHW
        )

    def graph(self):
        standard_params = self.get_standard_parameters()
        self.graph_button.setDisabled(True)
        graph_type = self.graph_type.currentText()
        if graph_type == GraphingWidget.ABSORPTION_COEFFICIENT_STRING:
            self.graph_abs_coef(standard_params)
        elif graph_type == GraphingWidget.ABSORPTION_SPECTRUM_STRING:
            self.graph_as(standard_params)
        elif graph_type == GraphingWidget.TRANSMITTANCE_SPECTRUM_STRING:
            self.graph_ts(standard_params)
        elif graph_type == GraphingWidget.RADIANCE_SPECTRUM_STRING:
            # Radiance spectrum
            self.graph_rs(standard_params)
        elif graph_type == GraphingWidget.BANDS_STRING:
            self.graph_bands(standard_params)

    def graph_abs_coef(self, standard_parameters):
        work = HapiWorker.echo(title=GraphingWidget.ABSORPTION_COEFFICIENT_STRING,
                               titlex="Wavenumber (cm<sup>-1</sup>)",
                               titley='Absorption Coefficient cm<sup>-1</sup>', **standard_parameters)

        if self.use_existing_window.isChecked():
            selected_window = self.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.ABSORPTION_COEFFICIENT, work)
                return

        self.parent.parent.add_child_window(GraphDisplayWindow(GraphType.ABSORPTION_COEFFICIENT, work, self))
        self.update_existing_window_items()

    def graph_as(self, standard_params):
        path_length = self.get_as_path_length()
        instrumental_fn = self.get_as_instrumental_fn()
        AF_wing = self.get_as_instrumental_fn_wing()
        Resolution = self.get_as_instrumental_resolution()

        if standard_params['WavenumberStep'] == None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title=GraphingWidget.ABSORPTION_SPECTRUM_STRING,
            titlex="Wavenumber (cm<sup>-1</sup>)",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )
        if self.use_existing_window.isChecked():
            selected_window = self.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.ABSORPTION_SPECTRUM, work)
                return

        self.parent.parent.add_child_window(GraphDisplayWindow(GraphType.ABSORPTION_SPECTRUM, work, self))
        self.update_existing_window_items()

    def graph_rs(self, standard_params):
        path_length = self.get_rs_path_length()
        instrumental_fn = self.get_rs_instrumental_fn()
        AF_wing = self.get_rs_instrumental_fn_wing()
        Resolution = self.get_rs_instrumental_resolution()

        if standard_params['WavenumberStep'] == None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title=GraphingWidget.RADIANCE_SPECTRUM_STRING,
            titlex="Wavenumber (cm<sup>-1</sup>)",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )
        if self.use_existing_window.isChecked():
            selected_window = self.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.RADIANCE_SPECTRUM, work)
                return

        self.parent.parent.add_child_window(GraphDisplayWindow(GraphType.RADIANCE_SPECTRUM, work, self))
        self.update_existing_window_items()

    def graph_ts(self, standard_params):
        path_length = self.get_ts_path_length()
        instrumental_fn = self.get_ts_instrumental_fn()
        AF_wing = self.get_ts_instrumental_fn_wing()
        Resolution = self.get_ts_instrumental_resolution()

        if standard_params['WavenumberStep'] == None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title=GraphingWidget.TRANSMITTANCE_SPECTRUM_STRING,
            titlex="Wavenumber (cm<sup>-1</sup>)",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )
        if self.use_existing_window.isChecked():
            selected_window = self.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.TRANSMITTANCE_SPECTRUM, work)
                return

        self.parent.parent.add_child_window(GraphDisplayWindow(GraphType.TRANSMITTANCE_SPECTRUM, work, self))
        self.update_existing_window_items()

    def graph_bands(self, standard_params):
        work = HapiWorker.echo(TableName=self.get_data_name(), title="Bands")
        if self.use_existing_window.isChecked():
            selected_window = self.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.BANDS, work)
                return
        self.parent.parent.add_child_window(GraphDisplayWindow(GraphType.BANDS, work, self))
        self.update_existing_window_items()

    def populate_data_names(self):
        """
        Retreive data file names from users data folder for display in the Graphing Window.
        """
        try:
            list(map(lambda name: self.data_name.addItem(name), get_all_data_names()))
        except Exception as e:
            err_log("Failed to populate data names, encountered error \'{}\'".format(str(e)))

    def done_graphing(self):
        """
        Re-enables buttons for use after graphing is finished.
        """
        self.graph_button.setEnabled(True)

    ##
    # Getters
    ##

    def get_diluent(self):
        """
        :returns: a dictionary containing all of the broadening parameters (currently, that is just gamma_air and gamma_self).
        """
        gamma_air = self.gamma_air.value()
        return {'air': gamma_air, 'self': 1.0 - gamma_air}

    def get_data_name(self):
        """
        :returns: name of the selected table
        """
        return self.data_name.currentText()

    def get_line_profile(self):
        return self.line_profile.currentText()

    def get_graph_type(self):
        """
        :returns: the type of graph selected
        """
        return self.graph_type.currentText()

    def get_intensity_threshold(self):
        """
        :returns: the intensity threshold input by the user, if there is one. If there was none, he default is returned
        """
        if self.intensity_threshold_enabled.checkState() == QtCore.Qt.Checked:
            return self.intensity_threshold.value()
        else:
            return DefaultIntensityThreshold

    def get_wn_range(self):
        """
        :returns: a tuple containing first the minimum wave number, second the maximum wave number
        """
        return (self.wn_min.value(), self.wn_max.value())

    def get_wn_step(self):
        """
        :returns: the wave number step if it was input by the user, otherwise it returns None and lets hapi decide the
                 default value.
        """
        if self.wn_step_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_step.value()
        else:
            return None

    def get_wn_wing(self):
        """
        :returns: the wave number wing if it was input by the user, otherwise it returns None and lets hapi decide the
                 default value.
        """
        if self.wn_wing_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_wing.value()
        else:
            return None

    def get_wn_wing_hw(self):
        """
        :returns: the wave number half-width if one was input by the user, otherwise it returns None and lets hapi
                 decide the default value
        """
        if self.wn_wing_hw_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_wing_hw.value()
        else:
            return None

    def get_temp(self):
        """
        :returns: the temperature parameter
        """
        return self.temperature.value()

    def get_pressure(self):
        """
        :returns: the pressure parameter
        """
        return self.pressure.value()

    def get_as_instrumental_fn(self):
        """
        :returns: Absorption spectrum instrumental fn
        """
        return self.as_instrumental_fn.currentText()

    def get_ts_instrumental_fn(self):
        """
        :returns: the Transmittance spectrum instrumental fn
        """
        return self.ts_instrumental_fn.currentText()

    def get_rs_instrumental_fn(self):
        """
        :returns: the Radiance spectrum instrumental fn
        """
        return self.rs_instrumental_fn.currentText()

    def get_rs_path_length(self):
        """
        :returns: the radiance spectrum path length
        """
        return self.rs_path_length.value()

    def get_ts_path_length(self):
        """
        :returns: the transmittance spectrum path length
        """
        return self.ts_path_length.value()

    def get_as_path_length(self):
        """
        :returns: the absorbtion spectrum path length
        """
        return self.as_path_length.value()

    def get_as_instrumental_fn_wing(self):
        """
        :returns: the absorbtion spectrum instrumental fn wing
        """
        return self.as_instrumental_fn_wing.value()

    def get_as_instrumental_resolution(self):
        """
        :returns: the absorbtion spectrum resolution
        """
        return self.as_instrumental_resolution.value()

    def get_ts_instrumental_fn_wing(self):
        """
        :returns: the transmittance spectrum fn wing
        """
        return self.ts_instrumental_fn_wing.value()

    def get_ts_instrumental_resolution(self):
        """
        :returns: the Transmittance spectrum resolution
        """
        return self.ts_instrumental_resolution.value()

    def get_rs_instrumental_fn_wing(self):
        """
        :returns: the radiance spectrum instrumental fn wing
        """
        return self.rs_instrumental_fn_wing.value()

    def get_rs_instrumental_resolution(self):
        """
        :returns: the radiance spectrum resolution
        """
        return self.rs_instrumental_resolution.value()

    def set_graph_buttons_enabled(self, enabled):
        """
        Enables all graph buttons.
        """
        self.graph_button.setEnabled(enabled)

    ##
    #   Utility Functions
    ###

    def remove_worker_by_jid(self, jid: int):
        for worker in self.workers:
            if worker.job_id == jid:
                worker.safe_exit()
                break

    parameters_required_to_graph = ['molec_id', 'local_iso_id', 'nu', 'sw', 'a', 'elower', 'gamma_air', 'delta_air',
                                    'gamma_self', 'n_air', 'gp', 'gpp']

    def update_existing_window_items(self):
        self.selected_window.clear()
        graph_ty_str = self.get_graph_type()
        if graph_ty_str == '':
            fitting_graph_windows = []
        else:
            graph_ty = GraphingWidget.str_to_graph_ty[graph_ty_str]

            fitting_graph_windows = list(builtins.filter(lambda window:
                                                         window.graph_ty == graph_ty,
                                                         GraphDisplayWindow.graph_windows.values()))

        if len(fitting_graph_windows) == 0:
            self.use_existing_window.setDisabled(True)
            self.selected_window.setDisabled(True)
            self.use_existing_window.setChecked(False)
            return

        list(map(lambda x: self.selected_window.addItem(str(x.window_id), None), fitting_graph_windows))
        self.use_existing_window.setEnabled(True)
        self.use_existing_window.setEnabled(True)

    def populate_graph_types(self):
        self.graph_type.addItem(GraphingWidget.ABSORPTION_SPECTRUM_STRING)
        self.graph_type.addItem(GraphingWidget.RADIANCE_SPECTRUM_STRING)
        self.graph_type.addItem(GraphingWidget.TRANSMITTANCE_SPECTRUM_STRING)
        self.graph_type.addItem(GraphingWidget.ABSORPTION_COEFFICIENT_STRING)
        self.graph_type.addItem(GraphingWidget.BANDS_STRING)

    ###
    #   Handlers
    ####

    def __on_graph_type_changed(self, graph_type):
        self.update_existing_window_items()

        self.line_profile_layout.setEnabled(True)
        self.wn_layout.setEnabled(True)
        self.wn_cfg_layout.setEnabled(True)
        self.plot_title_layout.setEnabled(True)
        self.graph_button_layout.setEnabled(True)
        self.window_layout.setEnabled(True)
        self.data_name_layout.setEnabled(True)
        self.env_layout.setEnabled(True)
        self.mixing_ratio_layout.setEnabled(True)
        self.graph_type_layout.setEnabled(True)

        if graph_type == GraphingWidget.ABSORPTION_COEFFICIENT_STRING:
            self.spectrum_tabs.setDisabled(True)
        elif graph_type == GraphingWidget.ABSORPTION_SPECTRUM_STRING:
            self.spectrum_tabs.setEnabled(True)
            self.absorbtion.setEnabled(True)
            self.spectrum_tabs.setCurrentWidget(self.absorbtion)
            self.transmittance.setDisabled(True)
            self.radiance.setDisabled(True)
        elif graph_type == GraphingWidget.TRANSMITTANCE_SPECTRUM_STRING:
            self.spectrum_tabs.setEnabled(True)
            self.transmittance.setEnabled(True)
            self.spectrum_tabs.setCurrentWidget(self.transmittance)
            self.absorbtion.setDisabled(True)
            self.radiance.setDisabled(True)
        elif graph_type == GraphingWidget.RADIANCE_SPECTRUM_STRING:
            self.spectrum_tabs.setEnabled(True)
            self.radiance.setEnabled(True)
            self.spectrum_tabs.setCurrentWidget(self.radiance)
            self.absorbtion.setDisabled(True)
            self.transmittance.setDisabled(True)
        elif graph_type == GraphingWidget.BANDS_STRING:
            self.line_profile_layout.setEnabled(False)
            self.wn_layout.setEnabled(False)
            self.line_profile_layout.setEnabled(False)
            self.wn_layout.setEnabled(False)
            self.wn_cfg_layout.setEnabled(False)
            self.env_layout.setEnabled(False)
            self.mixing_ratio_layout.setEnabled(False)

    def __handle_checkbox_toggle(self, checkbox, element):
        """
        A handler for checkboxes that will either enable or disable the corresponding element, depending on
        whether the checkbox is checked or not
        """
        if checkbox.isChecked():
            element.setEnabled(True)
        else:
            element.setDisabled(True)

    def __on_data_name_chagned(self, new_table):
        """
        Disables all graph buttons. (Inner method callback : enables graph buttons if necessary params to graph are supplied.)
        """
        self.set_graph_buttons_enabled(False)

        def callback(work_result):
            self.remove_worker_by_jid(work_result.job_id)
            result = work_result.result
            if result == None:
                return
            if 'parameters' not in result:
                self.set_graph_buttons_enabled(True)
                return
            for param in GraphingWidget.parameters_required_to_graph:
                if param not in result['parameters']:
                    err_log('Table does not contain required parameters.')
                    return
            self.wn_min.setValue(result['wn_min'])
            self.wn_max.setValue(result['wn_max'])

            self.set_graph_buttons_enabled(True)

        worker = HapiWorker(WorkRequest.TABLE_META_DATA, {'table_name': new_table}, callback)
        self.workers.append(worker)
        worker.start()

    def __on_gamma_air_changed(self, new_value: float):
        self.gamma_self.setText('{:8.4f}'.format(1.0 - new_value))
