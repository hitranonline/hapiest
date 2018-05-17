import PyQt5.QtCore
from utils.log import *
from widgets.graph_display_window_gui import *
from worker.hapi_worker import *
from worker.work_result import WorkResult
from windows.window import Window

class GraphDisplayWindow(Window):
    done_signal = QtCore.pyqtSignal(object)

    def __init__(self, ty, work_object, parent):
        """
        Initializes the GUI and sends a work request for the graph to be plotted, and connect signals to the
        appropriate handler methods.

        Args:
            ty:             the type of work to be done. May be different for different types of graphs.
            work_object:    has information about the graph that is to be made.
            parent:         the parent QObject.
        """
        super(GraphDisplayWindow, self).__init__(GraphDisplayWindowGui(), parent)
        
        self.worker = HapiWorker(ty, work_object, self.plot)
        self.worker.start()
        self.done_signal.connect(lambda: parent.done_graphing())
        self.gui.setWindowTitle(work_object['title'])
        self.open()


    def plot(self, work_result: WorkResult):
        """
        Plots the graph stored in 'work_result', which may be an error message rather than a result dictionary. If this
        is the case the error is printed to the console. This also emits a 'done' signal.

        Args:
            work_result:    the result of the HapiWorker; it will either be a string (which indicates an error), or it
                            will be a dictionary that contains the x and y coordinates and some information about graph
                            labels.
        """
        self.done_signal.emit(0)
        if type(work_result.result) != dict:
            err_log('Encountered error while graphing: ' + str(work_result.result))
            self.gui.loading_label.setText(
                '<span style="color:#aa0000;">' + 'Encountered error while graphing: \'' + str(
                    work_result.result) + '\'' + '</span>')
            return

        try:
            result = work_result.result
            (x, y) = result['x'], result['y']
            self.gui.add_graph(x, y, result['title'], result['titlex'], result['titley'])
        except Exception as e:
            err_log(e)

