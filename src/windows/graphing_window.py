from PyQt5 import QtCore

from utils.graph_type import GraphType
from utils.hapi_metadata import *
from widgets.graphing_window_gui import GraphingWindowGui
from windows.graph_display_window import *
from worker.hapi_worker import *
from utils.hapiest_util import *
from utils.log import *
from utils.graph_type import GraphType
from windows.window import Window
from windows.graph_display_window import GraphDisplayWindow

class GraphingWindow(Window):

    ABSORPTION_COEFFICIENT_STRING: str  = "Absorption Coefficient"
    ABSORPTION_SPECTRUM_STRING: str     = "Absorption Spectrum"
    TRANSMITTANCE_SPECTRUM_STRING: str  = "Transmittance Spectrum"
    RADIANCE_SPECTRUM_STRING: str       = "Radiance Spectrum"

    str_to_graph_ty = {
        ABSORPTION_COEFFICIENT_STRING:  GraphType.ABSORPTION_COEFFICIENT,
        ABSORPTION_SPECTRUM_STRING:     GraphType.ABSORPTION_SPECTRUM,
        TRANSMITTANCE_SPECTRUM_STRING:  GraphType.TRANSMITTANCE_SPECTRUM,
        RADIANCE_SPECTRUM_STRING:       GraphType.RADIANCE_SPECTRUM
    }

    def __init__(self, parent):
        """
        Populates Graphing Window with names of data files in users data folder, then initializes 
        Graphing Window to display options to the GUI corresponging to currently selected graph type 
        (Radiance, Absorption, or Transmittance Spectrum Graph types).
        
        """
        Window.__init__(self, GraphingWindowGui(), parent)
        try:
            self.populate_data_names()
        except Exception as e:
            print(e)

        def f():
            try:
                self.graph()
            except Exception as e:
                print(str(e))

        self.gui.graph_button.clicked.connect(lambda: f())
        
        self.open()

    
    def get_standard_parameters(self):
        data_name = self.gui.get_data_name()
        hmd = HapiMetaData(data_name)

        Components = hmd.iso_tuples
        SourceTables = [data_name]
        Environment = {'p': self.gui.get_pressure(), 'T': self.gui.get_temp()}
        Diluent = self.gui.get_diluent()
        WavenumberRange = self.gui.get_wn_range()
        WavenumberStep = self.gui.get_wn_step()
        WavenumberWing = self.gui.get_wn_wing()
        WavenumberWingHW = self.gui.get_wn_wing_hw()
        graph_fn = self.gui.get_line_profile()

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
        self.gui.graph_button.setDisabled(True)
        graph_type = self.gui.graph_type.currentText()
        if graph_type == GraphingWindow.ABSORPTION_COEFFICIENT_STRING:
            self.graph_abs_coef(standard_params)
        elif graph_type == GraphingWindow.ABSORPTION_SPECTRUM_STRING:
            self.graph_as(standard_params)
        elif graph_type == GraphingWindow.TRANSMITTANCE_SPECTRUM_STRING:
            self.graph_ts(standard_params)
        else:
            # Radiance spectrum
            self.graph_rs(standard_params)

    def graph_abs_coef(self, standard_parameters):
        work = HapiWorker.echo( title=GraphingWindow.ABSORPTION_COEFFICIENT_STRING, 
                                titlex="Wavenumber (cm<sup>-1</sup>)",
                                titley='Absorption Coefficient cm<sup>-1</sup>', **standard_parameters)

        if self.gui.use_existing_window.isChecked():
            selected_window = self.gui.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.ABSORPTION_COEFFICIENT, work)
                return

        self.add_child_window(GraphDisplayWindow(GraphType.ABSORPTION_COEFFICIENT, work, self))
        self.gui.update_existing_window_items()

    def graph_as(self, standard_params):
        """
        Formats GUI for Absorption Spectrum graphing.
        """
        path_length = self.gui.get_as_path_length()
        instrumental_fn = self.gui.get_as_instrumental_fn()
        AF_wing = self.gui.get_as_instrumental_fn_wing()
        Resolution = self.gui.get_as_instrumental_resolution()

        if standard_params['WavenumberStep'] == None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title=GraphingWindow.ABSORPTION_SPECTRUM_STRING,
            titlex="Wavenumber (cm<sup>-1</sup>)",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )
        if self.gui.use_existing_window.isChecked():
            selected_window = self.gui.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.ABSORPTION_SPECTRUM, work)
                return

        self.add_child_window(GraphDisplayWindow(GraphType.ABSORPTION_SPECTRUM, work, self))
        self.gui.update_existing_window_items()

    def graph_rs(self, standard_params):
        """
        Formats GUI for Radiance spectrum graphing.
        """
        
        path_length = self.gui.get_rs_path_length()
        instrumental_fn = self.gui.get_rs_instrumental_fn()
        AF_wing = self.gui.get_rs_instrumental_fn_wing()
        Resolution = self.gui.get_rs_instrumental_resolution()

        if standard_params['WavenumberStep'] == None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title=GraphingWindow.RADIANCE_SPECTRUM_STRING,
            titlex="Wavenumber (cm<sup>-1</sup>)",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )
        if self.gui.use_existing_window.isChecked():
            selected_window = self.gui.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.RADIANCE_SPECTRUM, work)
                return

        self.add_child_window(GraphDisplayWindow(GraphType.RADIANCE_SPECTRUM, work, self))
        self.gui.update_existing_window_items()

    def graph_ts(self, standard_params):
        """
        Formats GUI for Transmittance spectrum graping.
        """

        path_length = self.gui.get_ts_path_length()
        instrumental_fn = self.gui.get_ts_instrumental_fn()
        AF_wing = self.gui.get_ts_instrumental_fn_wing()
        Resolution = self.gui.get_ts_instrumental_resolution()

        if standard_params['WavenumberStep'] == None:
            standard_params['WavenumberStep'] = Resolution / 2
        elif standard_params['WavenumberStep'] <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title=GraphingWindow.TRANSMITTANCE_SPECTRUM_STRING,
            titlex="Wavenumber (cm<sup>-1</sup>)",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )
        if self.gui.use_existing_window.isChecked():
            selected_window = self.gui.selected_window.currentText()
            if selected_window in GraphDisplayWindow.graph_windows:
                GraphDisplayWindow.graph_windows[selected_window].add_worker(GraphType.TRANSMITTANCE_SPECTRUM, work)
                return

        self.add_child_window(GraphDisplayWindow(GraphType.TRANSMITTANCE_SPECTRUM, work, self))
        self.gui.update_existing_window_items()

    def populate_data_names(self):
        """
        Retreive data file names from users data folder for display in the Graphing Window.
        """
        try:
            data_names = get_all_data_names()
            for item in data_names:
                self.gui.data_name.addItem(item)

        except Exception as e:
            err_log("Failed to populate data names...")

    def done_graphing(self):
        """
        Re-enables buttons for use after graphing is finished.
        """
        self.gui.graph_button.setEnabled(True)
