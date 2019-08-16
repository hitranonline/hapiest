import json
from typing import *

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QOpenGLWidget, QLabel, QMainWindow, QFileDialog, QAction

from utils.colors import Colors
from utils.hapiest_util import *
from utils.log import *
from widgets.graphing.mpl_widget import MplWidget
from widgets.graphing.vispy_widget import VispyWidget
from worker.hapi_worker import HapiWorker, WorkResult
from worker.work_request import WorkRequest

from widgets.graphing.graph_type import GraphType

class GraphDisplayWidget(QMainWindow):
    done_signal = QtCore.pyqtSignal(object)


    graph_ty_to_work_ty = {
            GraphType.ABSORPTION_COEFFICIENT:   WorkRequest.ABSORPTION_COEFFICIENT,
            GraphType.TRANSMITTANCE_SPECTRUM:   WorkRequest.TRANSMITTANCE_SPECTRUM,
            GraphType.RADIANCE_SPECTRUM:        WorkRequest.RADIANCE_SPECTRUM,
            GraphType.ABSORPTION_SPECTRUM:      WorkRequest.ABSORPTION_SPECTRUM,
            GraphType.BANDS:                    WorkRequest.BANDS,
            # The abs coef work function also works for cross sectioons
            GraphType.XSC:                      WorkRequest.ABSORPTION_COEFFICIENT
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
        self.n_plots = 0
        self.plots = {}

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
        self.as_json: QAction = None


        uic.loadUi('layouts/graph_display_window.ui', self)

        self.as_json.triggered.connect(self.__on_save_as_json_triggered)
        self.as_csv.triggered.connect(self.__on_save_as_csv_triggered)

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
            sanitized_name = str(result['name']) \
                .replace(',', '') \
                .replace('\'', '') \
                .replace('"', '')
            self.plots[sanitized_name] = (x, y)
            if len(x) > len(y):
                x = x[:len(y)]
            elif len(x) < len(y):
                y = y[:len(x)]
            self.n_plots += 1
            self.backend.add_graph(x, y, result['title'], result['titlex'], result['titley'],
                                   f"{result['name']} - {self.n_plots}", result['args'])
        except Exception as e:
            err_log(e)

    def get_file_save_name(self, extension, filter) -> Union[str, None]:
        filename = QFileDialog.getSaveFileName(self, "Save as", "./data" + extension, filter)
        if filename[0] == "":
            return None
        else:
            return str(filename[0])

    def __on_save_as_json_triggered(self, _checked: bool):
        if len(self.plots) == 0:
            return

        filename = self.get_file_save_name(".json", "Javascript Object Notation (*.json)")
        if filename is None:
            return

        def to_x_y_arrays(series):
            (x, y) = series
            return {'x': x, 'y': y}

        d = {}
        for name, coords in self.plots.items():
            x, y = coords
            d[name] = {'x': list(x), 'y': list(y)}
        try:
            with open(filename, 'w') as file:
                file.write(json.dumps(d, indent=4))
        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))

    def __on_save_as_csv_triggered(self, _checked: bool):
        if len(self.plots) == 0:
            return

        filename = self.get_file_save_name(".csv", "Comma separated value files (*.csv)")

        if filename is None:
            return

        try:
            point_vectors = []
            order = list(self.plots.keys())
            lens = list(map(lambda plot_name: len(self.plots[plot_name][0]), order))
            max_len = max(lens)
            with open(filename, "w") as file:
                s = ''
                for name in order:
                    s += ' x_{:23s}, y_{:23s},'.format(name, name)
                file.write('{}\n'.format(s))

                for point_index in range(0, max_len):
                    s = ''
                    for i, name in enumerate(order):
                        if point_index >= lens[i]:
                            s = '{} {:14s}, {:14s},'.format(s, '', '')
                        else:
                            s = '{} {:14s}, {:14s},'.format(s,
                                                            str(self.plots[name][0][point_index]),
                                                            str(self.plots[name][1][point_index]))

                    file.write('{}\n'.format(s))

        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))