import functools
import math
from itertools import cycle
from time import sleep

from PyQt5 import QtGui
from PyQt5.QtChart import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow
from graphing.graph_type import GraphType
from graphing.hapi_series import HapiSeries

from data_structures.bands import Bands
from metadata.config import Config
from utils.colors import Colors
from utils.log import *
from widgets.graphing.band_legend import BandLegend, LegendItem
from widgets.graphing.graph_display_window_gui import GraphDisplayWindowGui
from widgets.graphing.hapi_chart_view import HapiChartView


class BandDisplayWindowGui(GraphDisplayWindowGui):

    def __init__(self):
        GraphDisplayWindowGui.__init__(self, GraphType.BANDS, "Bands")
        self.setting = False

    def closeEvent(self, event):
        self.legend.close()
        QMainWindow.closeEvent(self, event)

    def all_series(self):
        if self.highlighted_point is None:
            start = []
        else:
            start = [self.highlighted_point]
        return list(functools.reduce(list.__add__, self.band_series.values(), start))

    def add_bands(self, bands: Bands):
        if self.chart == None:
            series = []
            for band in bands.bands:
                cur_series = HapiSeries(band.x, band.y)
                cur_series.setName(band.band_id)

                series.append(cur_series)
                cur_series.hovered.connect(lambda point, state:
                                           self.__on_series_hover(cur_series, point, state))
                cur_series.setName(band.band_id)
                cur_series.setUseOpenGL(True)

            self.chart = QChart()
            self.band_series = { }
            self.legend = BandLegend(self.chart)

            self.chart.legend().setVisible(False)

            if self.axisy:
                self.chart.removeAxis(self.axisy)
                self.chart.removeAxis(self.axisx)

            self.axisx = QValueAxis()
            self.axisx.setTickCount(Config.axisx_ticks)
            self.axisx.setTitleText("Wavenumber (cm<sup>-1</sup>)")
            self.chart.addAxis(self.axisx, QtCore.Qt.AlignBottom)

            self.axisy_type = "log"
            self.axisy = QLogValueAxis()
            self.axisy.setTitleText("cm<sup>2</sup>/molecule")
            # setMinorTickCount is not supported in older versions of pyqtchart (< 5.9?)
            # self.axisy.setMinorTickCount(5)
            self.axisy.setBase(10.0)
            self.axisy.setLabelFormat(Config.axisy_log_label_format)
            self.chart.setAxisY(self.axisy)
            # self.chart.addAxis(self.axisy, QtCore.Qt.AlignLeft)

            self.chart_view = HapiChartView(self)
            self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
            self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

            self.chart.zoomReset()

            self.loading_label.setDisabled(True)
            self.graph_container.layout().addWidget(self.chart_view)
            self.graph_container.layout().addWidget(self.point_label)
            self.graph_container.layout().removeWidget(self.loading_label)

            self.legend.show()
        else:
            series = []
            color = QColor(self.colors.next())

            for band in bands.bands:
                cur_series = HapiSeries(band.x, band.y)
                cur_series.series.setMarkerSize(LegendItem.NORMAL_WIDTH)

                series.append(cur_series)
                cur_series.hovered.connect(lambda point, state:
                                           self.__on_series_hover(cur_series, point, state))
                cur_series.setName(band.band_id)
                cur_series.setUseOpenGL(True)

        list(map(lambda s: s.add_to_chart(self.chart), series))
        self.chart.setTitle("Table '{}' Bands".format(bands.table_name))

        list(map(lambda args: args[0].setColor(QColor(args[1])), zip(series, cycle(Colors.colors))))

        self.legend.add_item(series, bands.table_name)
        if bands.table_name in self.band_series:
            self.band_series[bands.table_name] += series
        else:
            self.band_series[bands.table_name] = series

        brush = QBrush()

        for s in series:
            s.setWidth(LegendItem.NORMAL_WIDTH)
            new_brush = QBrush(brush)
            new_brush.setColor(s.color())
            s.setBrush(new_brush)
            s.attachAxis(self.axisx)
            s.attachAxis(self.axisy)

        for band in bands.bands:
            if self.view_xmin != None:
                self.view_xmin = min(min(band.x), self.view_xmin)
            else:
                self.view_xmin = min(band.x)

            if self.view_ymin != None:
                self.view_ymin = min(min(band.y), self.view_ymin)
            else:
                self.view_ymin = min(band.y)

            if self.view_xmax != None:
                self.view_xmax = max(max(band.x), self.view_xmax)
            else:
                self.view_xmax = max(band.x)

            if self.view_ymax != None:
                self.view_ymax = max(max(band.y), self.view_ymax)
            else:
                self.view_ymax = max(band.y)
        self.on_view_fit_triggered(True)

    def on_point_clicked(self):

        if self.chart == None:
            return

        if self.highlighted_point != None:
            self.chart.removeSeries(self.highlighted_point.series)

        sleep(0.1)

        self.graph_container.layout().addWidget(self.point_label)
        global_coord = QCursor.pos()
        widget_coord = self.chart_view.mapFromGlobal(global_coord)
        scene_coord = self.chart_view.mapToScene(widget_coord)
        chart_item_coord = self.chart.mapFromScene(scene_coord)
        point = self.chart.mapToValue(chart_item_coord)
        px, py = (point.x(), point.y())
        xscale = self.view_ymax - self.view_ymin

        def dist(p1, p2):
            x1, y1 = (p1.x() * xscale, p1.y())
            x2, y2 = (p2.x() * xscale, p2.y())
            a = x1 - x2
            a *= a
            b = y1 - y2
            b *= b
            return math.sqrt(a + b)

        x, y = None, None
        band = None
        min_series = None
        min_dist = 100000
        for series in self.all_series():
            if series == self.highlighted_point:
                continue
            points = series.pointsVector()
            for np in points:
                distance = dist(point, np)
                if distance < min_dist:
                    x, y = (np.x(), np.y())
                    band = series.name()
                    min_series = series
                    min_dist = distance

        if x == None:
            return

        self.highlighted_point = HapiSeries()
        for point in min_series.pointsVector():
            self.highlighted_point.append(point.x(), point.y())
        self.point_label.clear()
        self.point_label.setText(
            "<b>{:15s}</b> {}".format('Selected Band:' + ('&nbsp;' * 10), band))
        color = QColor(0, 0, 0)
        self.highlighted_point.add_to_chart(self.chart)
        self.highlighted_point.brush().setColor(color)
        self.highlighted_point.pen().setColor(color)
        self.highlighted_point.pen().setWidth(8)
        self.highlighted_point.attachAxis(self.axisx)
        self.highlighted_point.attachAxis(self.axisy)

    def __on_series_hover(self, series, point: QPointF, state: bool):
        if state:
            series.pen().setWidth(6)
        else:
            series.pen().setWidth(3)
