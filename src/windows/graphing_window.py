from PyQt5 import QtCore

from utils.graph_type import GraphType
from utils.hapi_metadata import *
from widgets.graphing_window_gui import GraphingWindowGui
from windows.graph_display_window import *
from worker.hapi_worker import *
from utils.hapiest_util import *
from utils.log import *
from windows.window import Window

class GraphingWindow(Window):
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
        self.gui.graph_rs_button.clicked.connect(self.graph_rs)
        self.gui.graph_as_button.clicked.connect(self.graph_as)
        self.gui.graph_ts_button.clicked.connect(self.graph_ts)
        
        self.open()

    
    def get_standard_parameters(self):
        data_name = self.gui.get_data_name()
        hmd = HapiMetaData(data_name)

        Components = hmd.iso_tuples
        SourceTables = data_name
        Environment = {'p': self.gui.get_pressure(), 'T': self.gui.get_temp()}
        Diluent = self.gui.get_diluent()
        WavenumberRange = self.gui.get_wn_range()
        WavenumberStep = self.gui.get_wn_step()
        WavenumberWing = self.gui.get_wn_wing()
        WavenumberWingHW = self.gui.get_wn_wing_hw()
        graph_fn = self.gui.get_graph_type()

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
        self.gui.graph_button.setDisabled(True)

        work = HapiWorker.echo(title='Absorption Coefficient', titlex='Wavenumber', titley='Intensity', **self.get_standard_parameters())

        self.add_child_window(GraphDisplayWindow(GraphType.ABSORPTION_COEFFICIENT, work, self))

    def graph_as(self):
        """
        Formats GUI for Absorption Spectrum graphing.
        """
        self.gui.graph_as_button.setDisabled(True)

        standard_params = self.get_standard_parameters()

        path_length = self.gui.get_as_path_length()
        instrumental_fn = self.gui.get_as_instrumental_fn()
        AF_wing = self.gui.get_as_instrumental_fn_wing()
        Resolution = self.gui.get_as_instrumental_resolution()

        if WavenumberStep == None:
            WavenumberStep = Resolution / 2
        elif WavenumberStep <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.gui.graph_as_button.setEnabled(True)
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title="Absorption Spectrum",
            titlex="Wavenumber",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )

        self.add_child_window(GraphDisplayWindow(GraphType.ABSORPTION_SPECTRUM, work, self))

    def graph_rs(self):
        """
        Formats GUI for Radiance spectrum graphing.
        """
        self.gui.graph_rs_button.setDisabled(True)

        standard_params = self.get_standard_parameters()
        
        path_length = self.gui.get_rs_path_length()
        instrumental_fn = self.gui.get_rs_instrumental_fn()
        AF_wing = self.gui.get_rs_instrumental_fn_wing()
        Resolution = self.gui.get_rs_instrumental_resolution()

        if WavenumberStep == None:
            WavenumberStep = Resolution / 2
        elif WavenumberStep <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.gui.graph_as_button.setEnabled(True)
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title="Radiance Spectrum",
            titlex="Wavenumber",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )

        self.add_child_window(GraphDisplayWindow(GraphType.RADIANCE_SPECTRUM, work, self))

    def graph_ts(self):
        """
        Formats GUI for Transmittance spectrum graping.
        """
        self.gui.graph_ts_button.setDisabled(True)

        standard_params = self.get_standard_parameters()

        path_length = self.gui.get_ts_path_length()
        instrumental_fn = self.gui.get_ts_instrumental_fn()
        AF_wing = self.gui.get_ts_instrumental_fn_wing()
        Resolution = self.gui.get_ts_instrumental_resolution()

        if WavenumberStep == None:
            WavenumberStep = Resolution / 2
        elif WavenumberStep >= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.gui.graph_as_button.setEnabled(True)
            self.data_name_error.setText(
                '<span style="color:#aa0000;">' + 'Wavenumber Step must be less than the Instrumental Resolution' + '</span>')
            self.done_graphing()
            return

        work = HapiWorker.echo(
            title="Transmittance Spectrum",
            titlex="Wavenumber",
            titley="Intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing,
            **standard_params
        )

        self.add_child_window(GraphDisplayWindow(GraphType.TRANSMITTANCE_SPECTRUM, work, self))

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
        self.gui.graph_ts_button.setEnabled(True)
        self.gui.graph_rs_button.setEnabled(True)
        self.gui.graph_as_button.setEnabled(True)
