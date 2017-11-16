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
            type=Work.ABSORPTION_COEFFICIENT,
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
            self.children.append(GraphDisplayWindow(work, self))
        except Exception as e:
            debug(e)

    def populate_data_names(self):
        try:
            data_names = get_all_data_names()
            for item in data_names:
                self.gui.data_name.addItem(item)

        except Exception as e:
            err_log("Failed to populate data names...")

    def done_graphing(self):
        self.gui.graph_button.setEnabled(True)
