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


    def __init__(self, series, name, color):
        QFrame.__init__(self)

        self.setStyleSheet("""
        LegendItem {{
            border: 1px solid #{:x};
        }}
        """.format(color))

        self.series = series

        self.color_indicator = QWidget()
        self.color_indicator.setFixedSize(24, 24)
        self.color_indicator.setStyleSheet("""
        QWidget {{
            background-color: #{:x};
            border: 2px solid black;
        }}
        """.format(color))

        self.layout = QHBoxLayout()
        self.label = QLabel(name)
        self.label.setWordWrap(True)

        self.layout.addWidget(self.color_indicator)
        self.layout.addWidget(self.label)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(4, 4, 4, 4)

        self.setLayout(self.layout)
        
        self.on_hover_fn = lambda: ()

        self.installEventFilter(self)
        self.setMouseTracking(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            print('hey')
            pen = QPen()
            pen.setColor(self.series[0].pen().color())
            pen.setWidth(6)
            pen.setCosmetic(False)
            list(map(lambda series: series.setPen(pen), self.series))
            return True
        elif event.type() == QEvent.Leave:
            pen = QPen()
            pen.setColor(self.series[0].pen().color())
            pen.setWidth(3)
            pen.setCosmetic(False)
            list(map(lambda series: series.setPen(pen), self.series))
            return True
        return False

    def set_on_hover(self, on_hover_fn):
        self.on_hover_fn = on_hover_fn


class BandLegend(QWidget):


    def __init__(self):
        QWidget.__init__(self)
        layout = QHBoxLayout() #FlowLayout()
        self.setLayout(layout)

    def add_item(self, series, name, color):
        self.layout().addWidget(LegendItem(series, name, color))


