from widgets.graph_display_window_gui import GraphDisplayWindowGui
from PyQt5 import QtGui, QtWidgets, uic, QtCore
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *

from widgets.band_legend import BandLegend
from utils.band import Bands, Band
from utils.log import *
from utils.graph_type import GraphType
from typing import *


import functools
from random import randint


class BandDisplayWindowGui(GraphDisplayWindowGui):


    def __init__(self):
        GraphDisplayWindowGui.__init__(self, GraphType.BANDS, "Bands")

    def all_series(self):
        return functools.reduce(list.__add__, self.band_series.values(), [])

    def add_bands(self, bands: Bands):
        if self.chart == None:

            series = []
            color = QColor(self.colors.next())

            for band in bands.bands:
                cur_series = QLineSeries()
                cur_series.setColor(color)
                for i in range(0, len(band.x)):
                    cur_series.append(band.x[i], band.y[i])
         
                series.append(cur_series)
                cur_series.hovered.connect(lambda point, state:
                        self.__on_series_hover(cur_series, point, state))
                cur_series.setName(band.band_id)
                cur_series.setUseOpenGL(True)


            self.chart = QChart()
            self.band_series = {}
            self.legend = BandLegend()
            list(map(self.chart.addSeries, series))
            self.chart.setTitle("Table '{}' Bands".format(bands.table_name))

            self.legend.add_item(series, bands.table_name, color.rgb())
            self.chart.legend().setVisible(False)
            self.band_series[bands.table_name] = series

            if self.axisy:
                self.chart.removeAxis(self.axisy)
                self.chart.removeAxis(self.axisx)

            self.axisx = QValueAxis()
            self.axisx.setTickCount(5)
            self.axisx.setTitleText("Wavenumber (cm<sup>-1</sup>)")
            self.chart.addAxis(self.axisx, QtCore.Qt.AlignBottom)

            self.axisy = QValueAxis()
            self.axisy.setTitleText("Intensity")
            self.axisy.setTickCount(5)
            self.chart.addAxis(self.axisy, QtCore.Qt.AlignLeft)

            self.chart_view = QChartView(self.chart)
            self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
            self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

            self.loading_label.setDisabled(True)
            self.graph_container.layout().addWidget(self.chart_view)
            self.graph_container.layout().addWidget(self.legend)
            self.graph_container.layout().removeWidget(self.loading_label)
        else:
            series = []
            color = QColor(self.colors.next())

            for band in bands.bands:
                cur_series = QLineSeries()
                cur_series.setColor(color)
                for i in range(0, len(band.x)):
                    cur_series.append(band.x[i], band.y[i])

                series.append(cur_series)
                cur_series.hovered.connect(lambda point, state:
                        self.__on_series_hover(cur_series, point, state))
                cur_series.setName(band.band_id)
                cur_series.setUseOpenGL(True)


            list(map(self.chart.addSeries, series))
            self.chart.setTitle("Table '{}' Bands".format(bands.table_name))

            self.legend.add_item(series, bands.table_name, color.rgb())
            self.chart.legend().setVisible(False)
            self.band_series[bands.table_name] = series


        for s in series:
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
            series.pen().setWidth(4)
        else:
            series.pen().setWidth(1)
