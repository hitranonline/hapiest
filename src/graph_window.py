from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt
from PyQt5.QtChart import *
<<<<<<< HEAD
from util import * #edited src.
from config import * #edited src.
import numpy as np
from worker import * #edited src.
=======
from util import *
from config import *
import numpy as np
from worker import *
>>>>>>> origin/master

class GraphWindow():

    # Data should never be None / null, since if there is no data selected a new
    # graphing window shouldn't even be opened.
    def __init__(self, graph_fn):
        # graph_thread.start()
        self.gui = GraphWindowGui()
        self.graph_fn = graph_fn
        # graph_thread.join()
        # if len(graph_thread.errors) == 0:
        #     self.gui.add_graph(graph_thread.x, graph_thread.y)
        # else:
        #     for error in graph_thread.errors:
        #         err_(str(error))
        self.worker = Worker(self, self.graph_fn, self.plot)
        self.worker.start()

    def plot(self, data):
        debug("plot start")
        (x, y) = data
        try:
            self.gui.add_graph(x, y)
        except Exception as e:
            err_(e)
        debug("plot end")


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


class GraphWindowGui(QtWidgets.QWidget):

    def __init__(self):
        super(GraphWindowGui, self).__init__()
        if Config.high_dpi != 'true':
            uic.loadUi('layouts/graph_window.ui', self)
        else:
            uic.loadUi('layouts/graph_window.ui', self)

    def set_chart_title(self):
        pass

    def add_graph(self, x, y):
        layout = QtWidgets.QGridLayout()

        series = QLineSeries()
        for i in range(0, x.size):
            series.append(x[i], y[i])
        self.series = series
        series.setUseOpenGL(True)

        self.chart = QChart()
        self.chart.addSeries(series)
        self.chart.setTitle("Absorption Coefficient")

        self.axisx = QValueAxis()
        self.axisx.setTickCount(10)
        self.chart.addAxis(self.axisx, QtCore.Qt.AlignBottom)
        self.series.attachAxis(self.axisx)

        self.axisy = QValueAxis()
        self.axisy.setTickCount(10)
        self.chart.addAxis(self.axisy, QtCore.Qt.AlignLeft)
        self.series.attachAxis(self.axisy)

        self.chart.legend().hide()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

        layout.addWidget(self.chart_view)

        self.setLayout(layout)
        self.show()
