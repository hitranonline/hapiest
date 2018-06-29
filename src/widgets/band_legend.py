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


class LegendItem(QWidget):


    def __init__(self, all_series, name, r, g, b):
        QWidget.__init__(self)

        self.all_series = all_series

        self.color_indicator = QWidget()
        self.color_indicator.setGeometry(0, 0, 24, 24)
        self.color_indicator.setStyleSheet('background-color: #{:x}{:x}{:x}'.format(r, g, b))

        self.layout = QHBoxLayout()
        self.label = QLabel(name)
        self.label.setWordWrap(True)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.color_indicator)
        
        self.on_hover_fn = lambda: ()

        self.installEventFilter(self)
        self.setMouseTracking(True)


    def eventFilter(self, obj, event):
        if event.type() == QEvent.HoverEnter:
            for series in self.all_series:
                series.pen().setWidth(4)
        elif event.type() == QEvent.HoverLeave:
            for series in self.all_series:
                series.pen().setWidth(1)


    def set_on_hover(self, on_hover_fn):
        self.on_hover_fn = on_hover_fn


class BandLegend(QWidget):


    def __init__(self):
        QWidget.__init__(self)
        self.layout = FlowLayout()
        self.setLayout(layout)


    def add_item(self, all_series, name, r, g, b):
        self.layout.addItem(all_series, name, r, g, b)


