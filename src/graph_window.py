from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt
from PyQt5.QtChart import *
from hapiest_util import *
import hapiest_util
from config import *
import numpy as np
import worker


class GraphWindow(Qt.QObject):
    done_signal = QtCore.pyqtSignal(object)

    # Data should never be None / null, since if there is no data selected a new
    # graphing window shouldn't even be opened.
    def __init__(self, work_object, parent):
        Qt.QObject.__init__(self)
        self.parent = parent
        # graph_thread.start()
        self.gui = GraphWindowGui()
        # graph_thread.join()
        # if len(graph_thread.errors) == 0:
        #     self.gui.add_graph(graph_thread.x, graph_thread.y)
        # else:
        #     for error in graph_thread.errors:
        #         err_(str(error))
        self.worker = worker.HapiWorker(work_object, self.plot)
        self.worker.start()
        self.done_signal.connect(lambda: parent.done_graphing())

    def plot(self, data):
        self.done_signal.emit(0)
        try:
            (x, y) = (data['x'], data['y'])
            self.gui.add_graph(x, y, data['title'], data['titlex'], data['titley'])
        except Exception as e:
            hapiest_util.err_log(e)


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
        uic.loadUi('layouts/graph_window.ui', self)
        self.show()
        self.chart = None
        self.chart_view = None

        self.reset.clicked.connect(self.__on_zoom_reset_click)
        self.xmax.valueChanged.connect(lambda v: self.__on_xmax_changed(v))
        self.xmin.valueChanged.connect(lambda v: self.__on_xmin_changed(v))
        self.ymax.valueChanged.connect(lambda v: self.__on_ymax_changed(v))
        self.ymin.valueChanged.connect(lambda v: self.__on_ymin_changed(v))


    def set_chart_title(self):
        pass

    def add_graph(self, x, y, title="", xtitle="", ytitle=""):
        layout = QtWidgets.QGridLayout()

        series = QLineSeries()
        for i in range(0, x.size):
            series.append(x[i], y[i])
        self.series = series
        series.setUseOpenGL(True)

        self.chart = QChart()
        self.chart.addSeries(series)
        self.chart.setTitle(title)

        self.axisx = QValueAxis()
        self.axisx.setTickCount(5)
        self.axisx.setTitleText(xtitle)
        self.chart.addAxis(self.axisx, QtCore.Qt.AlignBottom)
        self.series.attachAxis(self.axisx)

        self.axisy = QValueAxis()
        self.axisy.setTitleText(ytitle)
        self.axisy.setTickCount(5)
        self.chart.addAxis(self.axisy, QtCore.Qt.AlignLeft)
        self.series.attachAxis(self.axisy)

        self.chart.legend().hide()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRubberBand(QChartView.NoRubberBand)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)


        layout.addWidget(self.chart_view)
        try:
            self.loading_label.setDisabled(True)
            self.graph_container.setLayout(layout)
        except Exception as e:
            print(e)

    def __on_zoom_reset_click(self):
        """

        :return:
        """
        if self.chart:
            self.chart.zoomReset()

    def __on_xmax_changed(self, value):
        min = self.xmin.value()
        if value < min:
            self.xmax.setValue(min)
            self.xmin.setValue(value)

    def __on_xmin_changed(self, value):
        max = self.xmax.value()
        if value > max:
            self.xmin.setValue(max)
            self.xmax.setValue(value)

    def __on_ymax_changed(self, value):
        min = self.ymin.value()
        if value < min:
            self.ymax.setValue(min)
            self.ymin.setValue(value)

    def __on_ymin_changed(self, value):
        max = self.ymax.value()
        if value > max:
            self.ymin.setValue(max)
            self.ymax.setValue(value)

    def __scene_event_handler(self, event):
        if event.type() == QtCore.QEvent.Gesture:
            self.__gesture_event_handler(event)

    def __gesture_event_handler(self, event):
        gesture = event.gesture(QtCore.Qt.PanGesture)
