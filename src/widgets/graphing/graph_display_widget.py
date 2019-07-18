from typing import *

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QOpenGLWidget, QLabel, QMainWindow

from graphing.graph_type import GraphType
from utils.colors import Colors
from utils.hapiest_util import *
from utils.log import *
from widgets.graphing.mpl_widget import MplWidget
from widgets.graphing.vispy_widget import VispyWidget
from worker.hapi_worker import HapiWorker, WorkResult
from worker.work_request import WorkRequest


class GraphDisplayWidget(QMainWindow):
    done_signal = QtCore.pyqtSignal(object)

    graph_ty_to_work_ty = {
            GraphType.ABSORPTION_COEFFICIENT:   WorkRequest.ABSORPTION_COEFFICIENT,
            GraphType.TRANSMITTANCE_SPECTRUM:   WorkRequest.TRANSMITTANCE_SPECTRUM,
            GraphType.RADIANCE_SPECTRUM:        WorkRequest.RADIANCE_SPECTRUM,
            GraphType.ABSORPTION_SPECTRUM:      WorkRequest.ABSORPTION_SPECTRUM,
            GraphType.BANDS:                    WorkRequest.BANDS
        }

    graph_windows = {}

    next_graph_graph_display_id = 1

    @staticmethod
    def graph_display_id():
        r = GraphDisplayWidget.next_graph_graph_display_id
        GraphDisplayWidget.next_graph_graph_display_id += 1
        return r

    @staticmethod
    def remove_child_window(graph_display_id: int):
        from widgets.graphing.graphing_widget import GraphingWidget

        if graph_display_id in GraphDisplayWidget.graph_windows:
            print(GraphDisplayWidget.graph_windows.pop(graph_display_id))
        GraphingWidget.GRAPHING_WIDGET_INSTANCE.update_existing_window_items()

    def __init__(self, graph_ty: GraphType, work_object: Dict, backend: str):
        """
        Initializes the GUI and sends a work request for the graph to be plotted, and connect
        signals to the appropriate handler methods.

        :param ty the type of graph to be calculated. May be different for different types of graphs
        :param work_object has information about the graph that is to be made
        :param parent the parent QObject

        """
        QMainWindow.__init__(self)

        self.graph_ty = graph_ty
        self.graph_display_id = GraphDisplayWidget.graph_display_id()
        self.workers = {
            0: HapiWorker(GraphDisplayWidget.graph_ty_to_work_ty[graph_ty], work_object,
                          lambda x: (self.plot(x), self.workers.pop(0)))
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

        self.setCentralWidget(self.backend)
        self.series = []

        self.setWindowTitle(f"Graphing window {self.graph_display_id}")
        self.show()

    def add_worker(self, graph_ty, work_object):
        id = self.cur_work_id
        self.cur_work_id += 1
        worker = HapiWorker(GraphDisplayWidget.graph_ty_to_work_ty[graph_ty], work_object,
                            lambda x: (self.plot(x), self.workers.pop(id)))

        self.workers[id] = worker
        worker.start()

    def closeEvent(self, event):
        self.close()
        event.accept()

    def reject(self):
        self.close()

    def close(self):
        """
        Overrides Window.close implementation, removes self from GraphDisplayWindow.graph_windows
        """
        from widgets.graphing.graphing_widget import GraphingWidget
        GraphDisplayWidget.graph_windows.pop(self.graph_display_id, None)
        GraphingWidget.GRAPHING_WIDGET_INSTANCE.update_existing_window_items()
        QMainWindow.close(self)

    def plot(self, work_result: WorkResult):
        """
        Plots the graph stored in 'work_result', which may be an error message rather than a result
        dictionary. If this is the case the error is printed to the console. This also emits a
        'done' signal.

        :param work_result the result of the HapiWorker; it will either be a string (which
        indicates an error), or it
                            will be a dictionary that contains the x and y coordinates and some
                            information about graph
                            labels
        """
        self.done_signal.emit(0)

        if type(work_result.result) != dict:
            err_log('Encountered error while graphing: ' + str(work_result.result))
            return

        try:
            result = work_result.result
            (x, y) = result['x'], result['y']
            self.backend.add_graph(x, y, result['title'], result['titlex'], result['titley'],
                                   result['name'], result['args'])
        except Exception as e:
            err_log(e)
