from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.band import Bands, Band
from utils.hapiest_util import *
from utils.log import *
from utils.graph_type import GraphType
from widgets.flow_layout import FlowLayout
from random import randint
from typing import *
import os
import json


class LegendItem(QFrame):


    def __init__(self, series, name, color, chart):
        QFrame.__init__(self)

        self.chart = chart
        self.series = series

        self.color_indicator = QWidget()
        self.color_indicator.setFixedSize(24, 24)
        self.color_indicator.setStyleSheet("""
        QWidget {{
            background-color: #{:x};
            border: 1px solid black;
        }}""".format(color))

        self.layout = QHBoxLayout()
        self.label = QLabel('table: {}'.format(name))
        self.label.setWordWrap(True)
        self.setLayout(self.layout)

        self.layout.addWidget(self.color_indicator)
        self.layout.addWidget(self.label)
        self.setStyleSheet("LegendItem {{ border: 2px solid #{:x}; }}".format(color))
        #"LegendItem { border: 2px solid #{:x}; }".format(color))

        self.on_hover_fn = lambda: ()

        self.installEventFilter(self)
        self.setMouseTracking(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            pen = QPen()
            pen.setColor(self.series[0].pen().color())
            pen.setWidth(6)
            pen.setCosmetic(False)
            list(map(lambda series: (series.setPen(pen), series.setWidth(20.0), series.setVisible(False), series.setVisible(True)), self.series))
            return True
        elif event.type() == QEvent.Leave:
            pen = QPen()
            pen.setColor(self.series[0].pen().color())
            pen.setWidth(3)
            pen.setCosmetic(False)
            list(map(lambda series: (series.setPen(pen), series.setWidth(10.0), series.setVisible(False), series.setVisible(True)), self.series))
            self.chart.update()
            return True
        return False

    def set_on_hover(self, on_hover_fn):
        self.on_hover_fn = on_hover_fn


class BandLegend(QWidget):


    def __init__(self, chart: QChart):
        QWidget.__init__(self)
        layout = QHBoxLayout() # FlowLayout()
        self.setLayout(layout)
        self.chart = chart

    def add_item(self, series, name, color):
        self.layout().addWidget(LegendItem(series, name, color, self.chart))


