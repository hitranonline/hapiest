from PyQt5 import QtGui, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QSplitter
from typing import Dict

from matplotlib.lines import Line2D

from graphing.graph_type import GraphType

from data_structures.bands import Bands
from utils.hapiest_util import program_icon
from utils.log import *
from widgets.graphing.band_legend import BandLegend
from widgets.graphing.graph_display_widget import GraphDisplayWidget
from widgets.graphing.mpl_widget import MplWidget
from widgets.graphing.vispy_widget import VispyWidget
from worker.hapi_worker import HapiWorker
from worker.work_result import WorkResult


class BandDisplayWidget(QMainWindow):
    done_signal = QtCore.pyqtSignal(object)

    def __init__(self, work_object: Dict, backend: str):
        QMainWindow.__init__(self, None)

        self.graph_ty = GraphType.BANDS

        self.legend = BandLegend(self)

        self.graph_display_id = GraphDisplayWidget.graph_display_id()
        self.workers = {
            0: HapiWorker(GraphDisplayWidget.graph_ty_to_work_ty[self.graph_ty], work_object,
                          lambda x: (self.plot_bands(x), self.workers.pop(0)))
            }

        GraphDisplayWidget.graph_windows[self.graph_display_id] = self

        self.workers[0].start()
        self.cur_work_id = 1

        from widgets.graphing.graphing_widget import GraphingWidget

        self.done_signal.connect(lambda: GraphingWidget.GRAPHING_WIDGET_INSTANCE.done_graphing())
        self.setWindowTitle(f"{work_object['title']} - {str(self.graph_display_id)}")

        self.setWindowIcon(program_icon())

        uic.loadUi('layouts/graph_display_window.ui', self)

        if backend == "matplotlib":
            self.backend = MplWidget(self)
        else:
            self.backend = VispyWidget(self)

        self.central_widget: QSplitter = QSplitter()
        self.central_widget.addWidget(self.backend)
        self.central_widget.addWidget(self.legend)
        self.setCentralWidget(self.central_widget)
        self.series = []

        self.setWindowTitle(f"Graphing window {self.graph_display_id}")
        self.show()

    def plot_bands(self, work_result: WorkResult):
        """
        Functions the same as `plot`, except this function is for plotting `Bands` objects
        """
        self.done_signal.emit(0)

        if type(work_result.result) != Bands:
            err_log("Encountered an error while generating bands: " + str(work_result))
            return

        bands: Bands = work_result.result

        bid2line: Dict[str, Line2D] = {}

        for band in bands.bands:
            bid2line[band.band_id] = self.backend.add_band(band.x, band.y)

        self.legend.add_bands(bid2line, bands.table_name)

    def closeEvent(self, event):
        self.legend.close()
        QMainWindow.closeEvent(self, event)

    def update_plot(self):
        """
        Update calls are slow in matplotlib, so don't call this more often than necessary.
        """
        self.backend.update_canvas()
