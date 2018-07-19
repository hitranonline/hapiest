from typing import List

from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QCheckBox

from utils.graphing.hapi_series import HapiSeries
from utils.hapiest_util import *


class LegendItem(QFrame):

    SELECTED_WIDTH = 8
    NORMAL_WIDTH = 3


    def __init__(self, bands: List[HapiSeries], name, chart):
        QFrame.__init__(self)

        self.chart = chart
        self.bands = bands

        self.band_layouts = []

        for band in self.bands:
            color_indicator = QWidget()
            color_indicator.setFixedSize(24, 24)
            color_indicator.setStyleSheet("""
            QWidget {{
                background-color: #{:x};
                border: 1px solid black;
            }}
            """.format(band.color()))

            toggle = QCheckBox()
            toggle.toggled.connect(lambda checked: band.setVisible(not checked))

            label = QLabel(band.series.name())

            layout = QHBoxLayout()

            layout.addWidget(toggle)
            layout.addWidget(color_indicator)
            layout.addWidget(label)

            self.band_layouts.append({
                'label': label,
                'layout': layout,
                'toggle': toggle,
                'color_indicator': color_indicator
            })

        self.toggle_all_layout = QHBoxLayout()
        self.toggle_all = QCheckBox()

        def on_toggle_all_toggled(checked: bool):
            for band_layout in self.band_layouts:
                band_layout['toggle'].setChecked(checked)

        self.label = QLabel('table: {}'.format(name))
        self.label.setWordWrap(True)
        self.toggle_all_layout.addWidget(self.toggle_all)
        self.toggle_all_layout.addWidget(self.label)
        self.toggle_all_layout.toggled.connect(on_toggle_all_toggled)

        self.layout = QVBoxLayout()

        self.layout.addLayout(self.toggle_all_layout)

        for band_item in self.band_layouts:
            self.layout.addLayout(band_item['layout'])

        self.setLayout(self.layout)

        self.layout.addWidget(self.color_indicator)
        self.layout.addWidget(self.label)
        self.setStyleSheet("LegendItem {{ border: 2px solid #{:x}; }}".format(color))
        #"LegendItem { border: 2px solid #{:x}; }".format(color))

        self.on_hover_fn = lambda: ()

        # self.installEventFilter(self)
        #self.setMouseTracking(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            pen = QPen()
            pen.setColor(self.bands[0].pen().color())
            pen.setWidth(6)
            pen.setCosmetic(False)
            list(map(lambda series: (series.setPen(pen), series.setWidth(20.0), series.setVisible(False), series.setVisible(True)), self.bands))
            return True
        elif event.type() == QEvent.Leave:
            pen = QPen()
            pen.setColor(self.series[0].pen().color())
            pen.setWidth(3)
            pen.setCosmetic(False)
            list(map(lambda series: (series.setPen(pen), series.setWidth(10.0), series.setVisible(False), series.setVisible(True)), self.bands))
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

    def add_item(self, bands, name):
        self.layout().addWidget(LegendItem(bands, name, self.chart))


