import PyQt5.QtCore
from utils.log import *
from widgets.graph_display_window_gui import *
from worker.hapi_worker import *
from worker.work_result import WorkResult


class GraphDisplayWindow(QtCore.QObject):
    done_signal = QtCore.pyqtSignal(object)

    # Data should never be None / null, since if there is no data selected a new
    # graphing window shouldn't even be opened.
    def __init__(self, type, work_object, parent):
        super(GraphDisplayWindow, self).__init__()
        self.parent = parent
        # graph_thread.start()
        self.gui = GraphDisplayWindowGui()
        # graph_thread.join()
        # if len(graph_thread.errors) == 0:
        #     self.gui.add_graph(graph_thread.x, graph_thread.y)
        # else:
        #     for error in graph_thread.errors:
        #         err_(str(error))
        self.worker = HapiWorker(type, work_object, self.plot)
        self.worker.start()
        self.done_signal.connect(lambda: parent.done_graphing())

    def plot(self, work_result: WorkResult):
        self.done_signal.emit(0)
        try:
            result = work_result.result
            (x, y) = result['x'], result['y']
            self.gui.add_graph(x, y, result['title'], result['titlex'], result['titley'])
        except Exception as e:
            err_log(e)

    def close(self):
        for window in self.child_windows:
            if window.is_open:
                window.close()
        self.gui.close()

    def open(self):
        self.gui.open()
