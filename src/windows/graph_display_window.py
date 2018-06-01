import PyQt5.QtCore
from utils.log import *
from widgets.graph_display_window_gui import *
from worker.hapi_worker import *
from worker.work_result import WorkResult
from worker.work_request import WorkRequest
from windows.window import Window
from utils.graph_type import GraphType

class GraphDisplayWindow(Window):
    done_signal = QtCore.pyqtSignal(object)
    
    graph_ty_to_work_ty = {
        GraphType.ABSORPTION_COEFFICIENT:   WorkRequest.ABSORPTION_COEFFICIENT,
        GraphType.TRANSMITTANCE_SPECTRUM:   WorkRequest.TRANSMITTANCE_SPECTRUM,
        GraphType.RADIANCE_SPECTRUM:        WorkRequest.RADIANCE_SPECTRUM,
        GraphType.ABSORPTION_SPECTRUM:      WorkRequest.ABSORPTION_SPECTRUM
    }

    graph_windows = {
       GraphType.ABSORPTION_COEFFICIENT:    {},
       GraphType.TRANSMITTANCE_SPECTRUM:    {},
       GraphType.RADIANCE_SPECTRUM:         {},
       GraphType.ABSORPTION_SPECTRUM:       {}  
    }

    next_graph_window_id = 1
    @staticmethod
    def window_id():
        r = GraphDisplayWindow.next_graph_window_id
        GraphDisplayWindow.next_graph_window_id += 1
        return r


    def __init__(self, graph_ty, work_object, parent):
        """
        Initializes the GUI and sends a work request for the graph to be plotted, and connect 
		signals to the appropriate handler methods.

        @param ty the type of graph to be calculated. May be different for different types of graphs
        @param work_object has information about the graph that is to be made
        @param parent the parent QObject
        
        """
        self.graph_ty = graph_ty
        self.window_id = GraphDisplayWindow.window_id()
        gui = GraphDisplayWindowGui(graph_ty, work_object['title'] + ' - ' + str(self.window_id))
        super(GraphDisplayWindow, self).__init__(gui, parent)

        GraphDisplayWindow.graph_windows[graph_ty][self.window_id] = self

        self.worker = HapiWorker(GraphDisplayWindow.graph_ty_to_work_ty[graph_ty], work_object, self.plot)
        self.worker.start()
        self.done_signal.connect(lambda: parent.done_graphing())
        self.gui.setWindowTitle(work_object['title'])
        self.open()

    
    def close(self):
        """
        Overrides Window.close implementation, removes self from GraphDisplayWindow.graph_windows
        """
        GraphDisplayWindow.graph_window[graph_ty].pop(self.window_id, None)

    def plot(self, work_result: WorkResult):
        """
        Plots the graph stored in 'work_result', which may be an error message rather than a result
		dictionary. If this is the case the error is printed to the console. This also emits a 'done' signal.

        @param work_result the result of the HapiWorker; it will either be a string (which indicates an error), or it
                            will be a dictionary that contains the x and y coordinates and some information about graph
                            labels
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

