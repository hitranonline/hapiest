from widgets.graph_display_window_gui import GraphDisplayWindowGui
from PyQt5 import QtGui, QtWidgets, uic, QtCore
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from widgets.band_legend import BandLegend
from utils.band import Bands, Band
from utils.hapiest_util import *
from utils.log import *
from utils.graph_type import GraphType
from widgets.gui import GUI
from random import randint
from typing import *
import os
import json

class BandDisplayWindowGui(GraphDisplayWindowGui):


    @staticmethod
    def generate_random_color(r, g, b):
        """
        @returns    a tuple, containing 3 integers between 0 and 255 which represent the r, g,
                    and b values of a color.
        """
        return ((randint(0, 255) + r) / 2, (randint(0, 255) + g) / 2, (randint(0, 255) + b) / 2)


    def __init__(self):
        GraphDisplayWindowGui.__init__(self)


    def add_bands(self, bands: Bands):
        if self.chart == None:
            self.chart = QChart()
            self.chart.setTitle("Table '{}' Bands".format(bands.table_name))
            self.band_series = {}
            self.legend = BandLegend()
            self.container.addWidget(self.legend)

            series = []
            r, g, b = BandDisplayWindowGui.generate_random_color(0x66, 0x66, 0x66)
            color = QColor(r, g, b)
            for band in bands.bands:
                cur_series = QLineSeries()
                cur_series.setColor(color)
                for i in range(0, len(band.x)):
                    cur_series.append(band.x[i], band.y[i])
         
                series.append(cur_series)
                series.hovered.connect(lambda point, state:
                        self.__on_series_hover(series, point, state))
                self.chart.addSeries(series)

            self.legend.add_item(series, bands.table_name, r, g, b)
            self.band_series[bands.table_name] = series
            series.setName(bands.table_name)
            series.setUseOpenGL(True)

            self.chart.legend().setVisible(False)

            if self.axisy:
                self.chart.removeAxis(self.axisy)
                self.chart.removeAxis(self.axisx)

            self.axisx = QValueAxis()
            self.axisx.setTickCount(5)
            self.axisx.setTitleText("Wavenumber (cm<sup>-1</sup>)")
            self.chart.addAxis(self.axisx, QtCore.Qt.AlignBottom)
            self.series[0].attachAxis(self.axisx)

            self.axisy = QValueAxis()
            self.axisy.setTitleText("Intensity")
            self.axisy.setTickCount(5)
            self.chart.addAxis(self.axisy, QtCore.Qt.AlignLeft)
            self.series[0].attachAxis(self.axisy)
            
            self.chart_view = QChartView(self.chart)
            self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
            self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

            layout = QtWidgets.QGridLayout()
            layout.addWidget(self.chart_view)
            self.loading_label.setDisabled(True)
            self.graph_container.setLayout(layout)
        else:
            series = []
            r, g, b = BandDisplayWindowGui.generate_random_color(0x66, 0x66, 0x66)
            color = QColor(r, g, b)
            for band in bands.bands:
                cur_series = QLineSeries()
                cur_series.setColor(color)
                for i in range(0, len(band.x)):
                    cur_series.append(band.x[i], band.y[i])
                
                series.attachAxis(self.axisy)
                series.attachAxis(self.axisx)
                series.setUseOpenGL(True)
                series.append(cur_series)
                series.hovered.connect(lambda point, state:
                        self.__on_series_hover(series, point, state))
                self.chart.addSeries(series)

            self.band_series[bands.table_name] = series
            self.legend.add_item(series, bands.table_name, r, g, b)
            self.band_series[bands.table_name] = series
            self.chart.addSeries(series)
        for band in bands.bands:
            if self.view_xmin:
                if self.view_xmin > band.x[0]:
                    self.view_xmin = band.x[0]
            else:
                self.view_xmin = self.axisx.min()
            if self.view_ymin:
                ymin = band.y[0]
                if self.view_ymin > ymin:
                    self.view_ymin = ymin
            else:
                self.view_ymin = self.axisy.min()
            if self.view_xmax:
                xmax = band.x[len(band.x) - 1]
                if self.view_xmax < xmax:
                    self.view_xmax = xmax
                else:
                    self.view_xmax = self.axisx.max()
            if self.view_ymax:
                ymax = band.y[len(band.y) - 1]
                if self.view_ymax < ymax:
                    self.view_ymax = ymax
            else:
                self.view_ymax = self.axisy.max()
            self.__on_view_fit_triggered(True)


    def __no_series_hover(self, series, point: QPointF, state: bool):
        if state:
            series.pen().setWidth(4)
        else:
            series.pen().setWidth(1)
