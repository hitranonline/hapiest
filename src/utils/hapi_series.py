from PyQt5 import QtChart
from PyQt5.QtChart import QLineSeries, QAbstractAxis, QChart
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen


class HapiSeries:

    def __init__(self, x = (), y = ()):
        if len(x) != 0:
            self.series = QLineSeries()
            for i in range(0, len(x)):
                # Since qt won't graph a chart using a log scale if there is a negative or zero value,
                # make sure everything is > 0.
                # This shouldn't be a problem since all of the graph types work with positive quantities.
                if y[i] < 1e-138:
                    continue
                self.append(x[i], y[i])
        else:
            self.series = QLineSeries()

        self.series.setUseOpenGL(True)

        self.hovered = self.series.hovered

    def add_to_chart(self, chart: QChart):
        chart.addSeries(self.series)

    def append(self, *args):
        self.series.append(*args)

    def internal_copy(self):
        """
        Makes a copy of the underlying series. This is needed because after removing a series from a chart,
        Qt deallocates the QLineSeries.
        """
        new_series = QLineSeries()
        for point in self.series.pointsVector():
            new_series.append(point.x(), point.y())
        self.series = new_series
        self.hovered = self.series.hovered

    def setPen(self, pen: QPen):
        self.series.setPen(pen)

    def pen(self) -> QPen:
        return self.series.pen()

    def setVisible(self, visible: bool):
        self.series.setVisible(visible)

    def setName(self, name: str):
        self.series.setName(name)

    def setUseOpenGL(self, use_opengl: bool):
        self.series.setUseOpenGL(use_opengl)

    def pointsVector(self):
        return self.series.pointsVector()

    def detachAxis(self, axis: QAbstractAxis):
        self.series.detachAxis(axis)

    def attachAxis(self, axis: QAbstractAxis):
        self.series.attachAxis(axis)
