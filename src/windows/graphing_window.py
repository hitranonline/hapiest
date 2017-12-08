from PyQt5 import QtCore

from utils.hapi_metadata import *
from widgets.graphing_window_gui import GraphingWindowGui
from windows.graph_display_window import *
from worker.hapi_worker import *
from utils.hapiest_util import *
from utils.log import *


class GraphingWindow(QtCore.QObject):
    def __init__(self, parent):
        super(GraphingWindow, self).__init__()
        self.parent = parent
        self.children = []
        self.gui = GraphingWindowGui()
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
        self.gui.graph_rs_button.clicked.connect(self.graph_rs)
        self.gui.graph_as_button.clicked.connect(self.graph_as)
        self.gui.graph_ts_button.clicked.connect(self.graph_ts)

    def graph(self):
        self.gui.graph_button.setDisabled(True)
        data_name = self.gui.get_data_name()
        hmd = HapiMetaData(data_name)

        Components = hmd.iso_tuples
        SourceTables = data_name
        Environment = {'p': self.gui.get_pressure(), 'T': self.gui.get_temp()}
        GammaL = self.gui.get_broadening_parameter()
        WavenumberRange = self.gui.get_wn_range()
        WavenumberStep = self.gui.get_wn_step()
        WavenumberWing = self.gui.get_wn_wing()
        WavenumberWingHW = self.gui.get_wn_wing_hw()
        graph_fn = self.gui.get_graph_type()

        work = HapiWorker.echo(
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

        self.children.append(GraphDisplayWindow(WorkRequest.ABSORPTION_COEFFICIENT, work, self))

    def graph_as(self):
        self.gui.graph_as_button.setDisabled(True)
        data_name = self.gui.get_data_name()
        hmd = HapiMetaData(data_name)

        Components = hmd.iso_tuples
        SourceTables = data_name
        Environment = {'p': self.gui.get_pressure(), 'T': self.gui.get_temp()}
        GammaL = self.gui.get_broadening_parameter()
        WavenumberRange = self.gui.get_wn_range()
        WavenumberStep = self.gui.get_wn_step()
        WavenumberWing = self.gui.get_wn_wing()
        WavenumberWingHW = self.gui.get_wn_wing_hw()
        graph_fn = self.gui.get_graph_type()
        path_length = self.gui.get_as_path_length()
        instrumental_fn = self.gui.get_as_instrumental_fn()
        AF_wing = self.gui.get_as_instrumental_fn_wing()
        Resolution = self.gui.get_as_instrumental_resolution()

        if WavenumberStep == None:
            WavenumberStep = Resolution / 2
        elif WavenumberStep <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.gui.graph_as_button.setEnabled(True)
            return

        work = HapiWorker.echo(
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
            title="Absorption Spectrum",
            titlex="wavenumber",
            titley="intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing
        )

        self.children.append(GraphDisplayWindow(WorkRequest.ABSORPTION_SPECTRUM, work, self))

    def graph_rs(self):
        """
        Radiance spectrum graphing.
        """
        self.gui.graph_rs_button.setDisabled(True)
        data_name = self.gui.get_data_name()
        hmd = HapiMetaData(data_name)

        Components = hmd.iso_tuples
        SourceTables = data_name
        Environment = {'p': self.gui.get_pressure(), 'T': self.gui.get_temp()}
        GammaL = self.gui.get_broadening_parameter()
        WavenumberRange = self.gui.get_wn_range()
        WavenumberStep = self.gui.get_wn_step()
        WavenumberWing = self.gui.get_wn_wing()
        WavenumberWingHW = self.gui.get_wn_wing_hw()
        graph_fn = self.gui.get_graph_type()
        path_length = self.gui.get_rs_path_length()
        instrumental_fn = self.gui.get_rs_instrumental_fn()
        AF_wing = self.gui.get_rs_instrumental_fn_wing()
        Resolution = self.gui.get_rs_instrumental_resolution()

        if WavenumberStep == None:
            WavenumberStep = Resolution / 2
        elif WavenumberStep <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.gui.graph_as_button.setEnabled(True)
            return

        work = HapiWorker.echo(
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
            title="Radiance Spectrum",
            titlex="wavenumber",
            titley="intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing
        )

        self.children.append(GraphDisplayWindow(WorkRequest.RADIANCE_SPECTRUM, work, self))

    def graph_ts(self):
        """
        Transmittance spectrum graping.
        """
        self.gui.graph_ts_button.setDisabled(True)
        data_name = self.gui.get_data_name()
        hmd = HapiMetaData(data_name)

        Components = hmd.iso_tuples
        SourceTables = data_name
        Environment = {'p': self.gui.get_pressure(), 'T': self.gui.get_temp()}
        GammaL = self.gui.get_broadening_parameter()
        WavenumberRange = self.gui.get_wn_range()
        WavenumberStep = self.gui.get_wn_step()
        WavenumberWing = self.gui.get_wn_wing()
        WavenumberWingHW = self.gui.get_wn_wing_hw()
        graph_fn = self.gui.get_graph_type()
        path_length = self.gui.get_ts_path_length()
        instrumental_fn = self.gui.get_ts_instrumental_fn()
        AF_wing = self.gui.get_ts_instrumental_fn_wing()
        Resolution = self.gui.get_ts_instrumental_resolution()

        if WavenumberStep == None:
            WavenumberStep = Resolution / 2
        elif WavenumberStep <= Resolution:
            err_log('Wavenumber Step must be less than Instrumental Resolution')
            self.gui.graph_as_button.setEnabled(True)
            return

        work = HapiWorker.echo(
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
            title="Transmittance Spectrum",
            titlex="wavenumber",
            titley="intensity",
            path_length=path_length,
            instrumental_fn=instrumental_fn,
            Resolution=Resolution,
            AF_wing=AF_wing
        )

        self.children.append(GraphDisplayWindow(WorkRequest.TRANSMITTANCE_SPECTRUM, work, self))

    def populate_data_names(self):
        try:
            data_names = get_all_data_names()
            for item in data_names:
                self.gui.data_name.addItem(item)

        except Exception as e:
            err_log("Failed to populate data names...")

    def done_graphing(self):
        self.gui.graph_button.setEnabled(True)
        self.gui.graph_ts_button.setEnabled(True)
        self.gui.graph_rs_button.setEnabled(True)
        self.gui.graph_as_button.setEnabled(True)
