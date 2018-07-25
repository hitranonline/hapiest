from PyQt5 import QtChart
from PyQt5.QtChart import QLineSeries, QAbstractAxis, QChart, QScatterSeries
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen, QBrush, QColor


class HapiSeries:

    def create_series(self):
        if self.use_scatter_plot:
            return QScatterSeries()
        return QLineSeries()

    def __init__(self, x = (), y = (), use_scatter_plot = True, name = ""):
        if len(x) != 0:
            self.use_scatter_plot = use_scatter_plot
            self.series = self.create_series()
            for i in range(0, len(x)):
                # Since qt won't graph a chart using a log scale if there is a negative or zero value,
                # make sure everything is > 0.
                # This shouldn't be a problem since all of the graph types work with positive quantities.
                if y[i] < 1e-138:
                    continue
                self.append(x[i], y[i])
        else:
            self.series = self.create_series()

        self.series.setName(name)

        self.series.setUseOpenGL(True)

        self.hovered = self.series.hovered

    def add_to_chart(self, chart: QChart):
        chart.addSeries(self.series)

    def append(self, *args):
        self.series.append(*args)

    def isVisible(self) -> bool:
        return self.series.isVisible()

    def internal_copy(self):
        """
        Makes a copy of the underlying series. This is needed because after removing a series from a chart,
        Qt deallocates the QLineSeries.
        """
        new_series = self.create_series()
        for point in self.series.pointsVector():
            new_series.append(point.x(), point.y())
        self.series = new_series
        self.hovered = self.series.hovered

    def setWidth(self, width: float):
        if self.use_scatter_plot:
            self.series.setMarkerSize(width)

    def setPen(self, pen: QPen):
        self.series.setPen(pen)

    def pen(self) -> QPen:
        return self.series.pen()

    def setBrush(self, brush: QBrush):
        self.series.setBrush(brush)

    def brush(self) -> QBrush:
        return self.series.brush()

    def color(self) -> QColor:
        return QColor(self.series.color())

    def setColor(self, color: QColor):
        self.series.setColor(color)

    def setVisible(self, visible: bool):
        self.series.setVisible(visible)

    def setName(self, name: str):
        self.series.setName(name)

    def name(self):
        return self.series.name()

    def setUseOpenGL(self, use_opengl: bool):
        self.series.setUseOpenGL(use_opengl)

    def pointsVector(self):
        return self.series.pointsVector()

    def detachAxis(self, axis: QAbstractAxis):
        self.series.detachAxis(axis)

    def attachAxis(self, axis: QAbstractAxis):
        self.series.attachAxis(axis)
