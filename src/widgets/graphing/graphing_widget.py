import builtins

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QComboBox, QLayout, QLabel, QDoubleSpinBox, QLineEdit, QPushButton, \
    QCheckBox, QFormLayout, QWidget
from graphing.graph_type import GraphType

from metadata.hapi_metadata import *
from utils.log import err_log
from widgets.graphing.band_display_widget import BandDisplayWidget
from widgets.graphing.graph_display_widget import GraphDisplayWidget
from worker.hapi_worker import HapiWorker
from worker.work_request import WorkRequest


class GraphingWidget(QtWidgets.QWidget):
    ABSORPTION_COEFFICIENT_STRING: str = "Absorption Coefficient"
    ABSORPTION_SPECTRUM_STRING: str = "Absorption Spectrum"
    TRANSMITTANCE_SPECTRUM_STRING: str = "Transmittance Spectrum"
    RADIANCE_SPECTRUM_STRING: str = "Radiance Spectrum"
    BANDS_STRING: str = "Bands"

    GRAPHING_WIDGET_INSTANCE = None

    str_to_graph_ty = {
        ABSORPTION_COEFFICIENT_STRING:  GraphType.ABSORPTION_COEFFICIENT,
        ABSORPTION_SPECTRUM_STRING:     GraphType.ABSORPTION_SPECTRUM,
        TRANSMITTANCE_SPECTRUM_STRING:  GraphType.TRANSMITTANCE_SPECTRUM,
        RADIANCE_SPECTRUM_STRING:       GraphType.RADIANCE_SPECTRUM,
        BANDS_STRING:                   GraphType.BANDS
        }

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self)

        if GraphingWidget.GRAPHING_WIDGET_INSTANCE is not None:
            raise Exception("Only one instance of GraphingWidget should be created")
        GraphingWidget.GRAPHING_WIDGET_INSTANCE = self

        self.parent = parent

        self.workers = []

        self.graph_type: QComboBox = None

        self.graph_button_layout: QLayout = None
        self.window_layout: QLayout = None
        self.data_name_layout: QLayout = None

        self.spectrum_parameters_widget: QWidget = None
        self.line_profile_widget: QWidget = None
        self.wn_widget: QWidget = None
        self.wn_cfg_widget: QWidget = None
        self.env_widget: QWidget = None
        self.mixing_ratio_widget: QWidget = None
        self.graph_type_widget: QWidget = None

        self.backend: QComboBox = None
        self.plot_name: QLineEdit = None
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
        self.numax: QDoubleSpinBox = None
        self.numin: QDoubleSpinBox = None
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


        self.path_length: QDoubleSpinBox = None
        self.instrumental_fn: QComboBox = None
        self.instrumental_fn_wing: QDoubleSpinBox = None
        self.instrumental_resolution: QDoubleSpinBox = None

        uic.loadUi('layouts/graphing_widget.ui', self)
        self.wn_step_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_step_enabled, self.wn_step))
        self.wn_wing_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_enabled, self.wn_wing))
        self.wn_wing_hw_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.wn_wing_hw_enabled, self.wn_wing_hw))
        self.intensity_threshold_enabled.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.intensity_threshold_enabled,
                                                  self.intensity_threshold))
        self.use_existing_window.toggled.connect(
            lambda: self.__handle_checkbox_toggle(self.use_existing_window, self.selected_window))

        self.graph_button.clicked.connect(self.graph)
        self.graph_type.currentTextChanged.connect(self.__on_graph_type_changed)
        self.data_name.currentTextChanged.connect(self.__on_data_name_changed)
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
        self.numin.setToolTip("Select min wavelength for graph.")
        self.numax.setToolTip("Select max wavelength for graph.")

        self.wn_step.setToolTip("Select increment for wave number (wn).")
        self.wn_wing.setToolTip(
            "Set distance from the center of each line to the farthest point where the "
            "profile is considered to be non zero.")
        self.wn_wing_hw.setToolTip("Set relative value of the line wing in halfwidths")

        self.adjustSize()

    def get_standard_parameters(self):
        data_name = self.get_data_name()
        backend = self.backend.currentText()

        if self.xsc is not None:
            Components = []
            SourceTables = [data_name]
            Environment = {'p': self.xsc.pressure, 'T': self.xsc.temp}
            WavenumberRange = (self.xsc.numin, self.xsc.numax)
            WavenumberStep = self.xsc.step
            Diluent = {'air': 0.0, 'self': 1.0}
            # TODO: Verify that these are the proper values.
            WavenumberWing = 0.0
            WavenumberWingHW = 0.0
        else:
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

        return HapiWorker.echo(graph_fn=graph_fn, Components=Components, SourceTables=SourceTables,
            Environment=Environment, Diluent=Diluent, HITRAN_units=False,
            WavenumberRange=WavenumberRange, WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing, WavenumberWingHW=WavenumberWingHW, backend=backend)

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
                               titlex="Wavenumber (cm$^{-1}$)",
                               titley='Absorption Coefficient ', **standard_parameters)

        if work['SourceTables'][0].endswith('.xsc'):
            work['titley'] = 'molecules / cm$^2$'
            work['title'] = 'Absorption Cross-Section'

        if self.use_existing_window.isChecked():
            selected_window = self.get_selected_window()
            if selected_window in GraphDisplayWidget.graph_windows:
                GraphDisplayWidget.graph_windows[selected_window].add_worker(
                    GraphType.ABSORPTION_COEFFICIENT, work)
                return

        GraphDisplayWidget(GraphType.ABSORPTION_COEFFICIENT, work, self.backend.currentText())

        self.update_existing_window_items()

    def graph_as(self, standard_params):
        path_length = self.get_path_length()
        instrumental_fn = self.get_instrumental_fn()
        AF_wing = self.get_instrumental_fn_wing()
        Resolution = self.get_instrumental_resolution()

        if standard_params['WavenumberStep'] is None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            standard_params[
                'WavenumberStep'] = Resolution * 1.0001  # err_log('Wavenumber Step must be less 
            # than Instrumental Resolution')  # self.done_graphing()  # return

        work = HapiWorker.echo(title=GraphingWidget.ABSORPTION_SPECTRUM_STRING,
            titlex="Wavenumber (cm$^{-1}$)", titley="Absorption Spectrum",
            path_length=path_length, instrumental_fn=instrumental_fn, Resolution=Resolution,
            AF_wing=AF_wing, **standard_params)
        if self.use_existing_window.isChecked():
            selected_window = self.get_selected_window()
            if selected_window in GraphDisplayWidget.graph_windows:
                GraphDisplayWidget.graph_windows[selected_window].add_worker(
                    GraphType.ABSORPTION_SPECTRUM, work)
                return

        GraphDisplayWidget(GraphType.ABSORPTION_SPECTRUM, work, self.backend.currentText())
        self.update_existing_window_items()

    def graph_rs(self, standard_params):
        path_length = self.get_path_length()
        instrumental_fn = self.get_instrumental_fn()
        AF_wing = self.get_instrumental_fn_wing()
        Resolution = self.get_instrumental_resolution()

        if standard_params['WavenumberStep'] == None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the '
                                                  'Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(title=GraphingWidget.RADIANCE_SPECTRUM_STRING,
            titlex="Wavenumber (cm$^{-1}$)",
            titley="Radiance (erg * c$^{-1}$*cm$^{-1}$)", path_length=path_length,
            instrumental_fn=instrumental_fn, Resolution=Resolution, AF_wing=AF_wing,
            **standard_params)
        if self.use_existing_window.isChecked():
            selected_window = self.get_selected_window()
            if selected_window in GraphDisplayWidget.graph_windows:
                GraphDisplayWidget.graph_windows[selected_window].add_worker(
                    GraphType.RADIANCE_SPECTRUM, work)
                return

        GraphDisplayWidget(GraphType.RADIANCE_SPECTRUM, work, self.backend.currentText())
        self.update_existing_window_items()

    def graph_ts(self, standard_params):
        path_length = self.get_path_length()
        instrumental_fn = self.get_instrumental_fn()
        AF_wing = self.get_instrumental_fn_wing()
        Resolution = self.get_instrumental_resolution()

        if standard_params['WavenumberStep'] == None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the '
                                                  'Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(title=GraphingWidget.TRANSMITTANCE_SPECTRUM_STRING,
            titlex="Wavenumber (cm$^{-1}$)", titley="Transmittance", path_length=path_length,
            instrumental_fn=instrumental_fn, Resolution=Resolution, AF_wing=AF_wing,
            **standard_params)
        if self.use_existing_window.isChecked():
            selected_window = self.get_selected_window()
            if selected_window in GraphDisplayWidget.graph_windows:
                GraphDisplayWidget.graph_windows[selected_window].add_worker(
                    GraphType.TRANSMITTANCE_SPECTRUM, work)
                return

        GraphDisplayWidget(GraphType.TRANSMITTANCE_SPECTRUM, work, self.backend.currentText())
        self.update_existing_window_items()

    def graph_bands(self, _standard_params):
        work = HapiWorker.echo(TableName=self.get_data_name(), title="Bands")
        if self.use_existing_window.isChecked():
            selected_window = self.get_selected_window()
            if selected_window in GraphDisplayWidget.graph_windows:
                GraphDisplayWidget.graph_windows[selected_window].add_worker(GraphType.BANDS, work)
                return
        BandDisplayWidget(work, self.backend.currentText())
        self.update_existing_window_items()

    def populate_data_names(self):
        """
        Retrieve data file names from users data folder for display in the Graphing Window.
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

    def get_selected_window(self):
        return int(self.selected_window.currentText())

    def __on_graph_type_changed(self, graph_type):
        self.update_existing_window_items()

        self.line_profile_widget.setEnabled(True)
        self.wn_widget.setEnabled(True)
        self.wn_cfg_widget.setEnabled(True)
        self.graph_button.setEnabled(True)
        self.env_widget.setEnabled(True)
        self.mixing_ratio_widget.setEnabled(True)
        self.graph_type_widget.setEnabled(True)

        if graph_type == GraphingWidget.ABSORPTION_COEFFICIENT_STRING:
            self.spectrum_parameters_widget.setEnabled(False)
        elif graph_type in {GraphingWidget.ABSORPTION_SPECTRUM_STRING,
                            GraphingWidget.TRANSMITTANCE_SPECTRUM_STRING,
                            GraphingWidget.RADIANCE_SPECTRUM_STRING}:
            self.spectrum_parameters_widget.setEnabled(True)
        elif graph_type == GraphingWidget.BANDS_STRING:
            self.wn_widget.setEnabled(False)
            self.line_profile_widget.setEnabled(False)
            self.wn_widget.setEnabled(False)
            self.wn_cfg_widget.setEnabled(False)
            self.env_widget.setEnabled(False)
            self.mixing_ratio_widget.setEnabled(False)
            self.spectrum_parameters_widget.setEnabled(False)

    def __handle_checkbox_toggle(self, checkbox, element):
        """
        A handler for checkboxes that will either enable or disable the corresponding element,
        depending on
        whether the checkbox is checked or not
        """
        if checkbox.isChecked():
            element.setEnabled(True)
        else:
            element.setDisabled(True)

    def __on_data_name_changed(self, new_table):
        """
        Disables all graph buttons. (Inner method callback : enables graph buttons if necessary
        params to graph are supplied.)
        """
        self.set_graph_buttons_enabled(False)
        self.same_window_checked = self.use_existing_window.isChecked()

        def callback(work_result):
            self.remove_worker_by_jid(work_result.job_id)
            result = work_result.result
            if result is None:
                return

            self.plot_name.setText(self.data_name.currentText())

            if 'parameters' not in result:
                self.set_graph_buttons_enabled(True)
                return

            if not result['xsc']:
                for param in GraphingWidget.parameters_required_to_graph:
                    if param not in result['parameters']:
                        err_log('Table does not contain required parameters.')
                        return

            self.numin.setValue(result['numin'])
            self.numax.setValue(result['numax'])
            self.set_graph_buttons_enabled(True)

            if result['xsc'] is not None:
                self.set_xsc_mode(True)
                self.graph_type.clear()
                self.graph_type.addItems([GraphingWidget.ABSORPTION_COEFFICIENT_STRING])
            else:
                self.set_xsc_mode(False)
                self.graph_type.clear()
                self.graph_type.addItems(list(GraphingWidget.str_to_graph_ty.keys()))

            self.xsc = result['xsc']
            self.use_existing_window.setChecked(self.same_window_checked)

        worker = HapiWorker(WorkRequest.TABLE_META_DATA, {'table_name': new_table}, callback)
        self.workers.append(worker)
        worker.start()

    def set_xsc_mode(self, xsc_mode):
        enabled = not xsc_mode
        self.gamma_air.setEnabled(enabled)
        self.gamma_self.setEnabled(enabled)
        self.numin.setEnabled(enabled)
        self.numax.setEnabled(enabled)
        self.wn_step_enabled.setEnabled(enabled)
        self.wn_step.setEnabled(enabled)
        self.wn_wing.setEnabled(enabled)
        self.wn_wing_enabled.setEnabled(enabled)
        self.wn_wing_hw.setEnabled(enabled)
        self.wn_wing_hw_enabled.setEnabled(enabled)
        self.intensity_threshold.setEnabled(enabled)
        self.intensity_threshold_enabled.setEnabled(enabled)
        self.spectrum_parameters_widget.setEnabled(enabled)
        self.temperature.setEnabled(enabled)
        self.pressure.setEnabled(enabled)
        self.line_profile.setEnabled(enabled)

    def __on_gamma_air_changed(self, new_value: float):
        self.gamma_self.setText('{:8.4f}'.format(1.0 - new_value))

    ##
    # Getters
    ##

    def get_diluent(self):
        """
        :returns: a dictionary containing all of the broadening parameters (currently,
        that is just gamma_air and gamma_self).
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
        :returns: the intensity threshold input by the user, if there is one. If there was none,
        he default is returned
        """
        if self.intensity_threshold_enabled.checkState() == QtCore.Qt.Checked:
            return self.intensity_threshold.value()
        else:
            return DefaultIntensityThreshold

    def get_wn_range(self):
        """
        :returns: a tuple containing first the minimum wave number, second the maximum wave number
        """
        return (self.numin.value(), self.numax.value())

    def get_wn_step(self):
        """
        :returns: the wave number step if it was input by the user, otherwise it returns None and
        lets hapi decide the
                 default value.
        """
        if self.wn_step_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_step.value()
        else:
            return None

    def get_wn_wing(self):
        """
        :returns: the wave number wing if it was input by the user, otherwise it returns None and
        lets hapi decide the
                 default value.
        """
        if self.wn_wing_enabled.checkState() == QtCore.Qt.Checked:
            return self.wn_wing.value()
        else:
            return None

    def get_wn_wing_hw(self):
        """
        :returns: the wave number half-width if one was input by the user, otherwise it returns
        None and lets hapi
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

    def get_instrumental_fn(self):
        """
        :returns: Absorption spectrum instrumental fn
        """
        return self.instrumental_fn.currentText()

    def get_path_length(self):
        """
        :return: the path length
        """
        return self.path_length.value()

    def get_instrumental_fn_wing(self):
        """
        :return: the absorbtion spectrum instrumental fn wing
        """
        return self.instrumental_fn_wing.value()

    def get_instrumental_resolution(self):
        """
        :return: the instrumental resolution
        """
        return self.instrumental_resolution.value()

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

    ##
    #  Parameters that are required to graph hapi tables. These are not required to graph bands.
    parameters_required_to_graph = ['molec_id', 'local_iso_id', 'nu', 'sw', 'a', 'elower',
                                    'gamma_air', 'delta_air', 'gamma_self', 'n_air', 'gp', 'gpp']

    def update_existing_window_items(self):
        self.selected_window.clear()
        graph_ty_str = self.get_graph_type()
        if graph_ty_str == '':
            fitting_graph_windows = []
        else:
            graph_ty = GraphingWidget.str_to_graph_ty[graph_ty_str]

            fitting_graph_windows = list(builtins.filter(lambda window: window.graph_ty == graph_ty,
                                                         GraphDisplayWidget.graph_windows.values()))

        if len(fitting_graph_windows) == 0:
            self.use_existing_window.setChecked(False)
            self.use_existing_window.setDisabled(True)
            self.selected_window.setDisabled(True)
            return

        list(map(lambda x: self.selected_window.addItem(str(x.graph_display_id), None),
                 fitting_graph_windows))
        self.use_existing_window.setEnabled(True)

    def populate_graph_types(self):
        self.graph_type.addItem(GraphingWidget.ABSORPTION_SPECTRUM_STRING)
        self.graph_type.addItem(GraphingWidget.RADIANCE_SPECTRUM_STRING)
        self.graph_type.addItem(GraphingWidget.TRANSMITTANCE_SPECTRUM_STRING)
        self.graph_type.addItem(GraphingWidget.ABSORPTION_COEFFICIENT_STRING)
        self.graph_type.addItem(GraphingWidget.BANDS_STRING)
