from window import Window
from PyQt4 import QtGui, uic, QtCore, Qt
from util import *

class GraphWindow(Window):

    # Data should never be None / null, since if there is no data selected a new
    # graphing window shouldn't even be opened.
    def __init__(self, data, graph_type):
        # Child windows of the graph window will be all the windows with graphs
        # it opens
        self.child_windows = []

        self.gui = GraphWindowGui(self, graph_type)
        self.graph_type = graph_type
        self.data = data
        self.is_open = True

    def try_render_graph(self):
        # TODO: Implement this
        pass

    def display_graph(self, graph):
        self.child_windows.append(graph)
        # TODO: Implement this

    def close(self):
        for window in self.child_windows:
            if window.is_open:
                window.close()
        self.gui.close()

    def open(self):
        self.gui.open()


class GraphWindowGui(QtGui.QWidget):

    def __init__(self):
            super(GraphWindowGui, self).__init__()
            if CONFIG.high_dpi != 'true':
                uic.loadUi('layouts/graph_window.ui', self)
            else:
                uic.loadUi('layouts/graph_window_high_dpi.ui', self)