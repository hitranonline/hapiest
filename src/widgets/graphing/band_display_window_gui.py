from itertools import cycle

from utils.graphics.colors import Colors
from utils.metadata.config import Config
from utils.graphing.hapi_series import HapiSeries
from widgets.graphing.graph_display_window_gui import GraphDisplayWindowGui
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *

from widgets.graphing.band_legend import BandLegend
from utils.graphing.band import Bands
from utils.log import *
from utils.graphing.graph_type import GraphType

import functools

from widgets.graphing.hapi_chart_view import HapiChartView


class BandDisplayWindowGui(GraphDisplayWindowGui):

    def __init__(self):
        GraphDisplayWindowGui.__init__(self, GraphType.BANDS, "Bands")

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
            self.band_series = {}
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
            self.axisy.setTitleText("Intensity Contribution")
            self.axisy.setMinorTickCount(5)
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
            self.graph_container.layout().removeWidget(self.loading_label)

            self.legend.show()
        else:
            series = []
            color = QColor(self.colors.next())

            for band in bands.bands:
                cur_series = HapiSeries(band.x, band.y)

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
            s.setWidth(4)
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

    def __on_series_hover(self, series, point: QPointF, state: bool):
        if state:
            series.pen().setWidth(6)
        else:
            series.pen().setWidth(3)
