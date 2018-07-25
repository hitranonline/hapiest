from typing import List

from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QCheckBox, QScrollArea, QSizePolicy

from utils.graphing.band import Band
from utils.graphing.hapi_series import HapiSeries
from utils.hapiest_util import *

class BandWidget(QWidget):

    def __init__(self, band: HapiSeries):
        QWidget.__init__(self)
        self.band = band

        self.color_indicator = QWidget()
        self.color_indicator.installEventFilter(self)
        self.color_indicator.setFixedSize(24, 24)
        self.color_indicator.setStyleSheet("""
        QWidget {{
            background-color: #{:x};
            border: 1px solid black;
        }}
        """.format(band.color().rgb()))

        self.toggle = QCheckBox()
        self.toggle.setChecked(True)
        self.toggle.toggled.connect(self.hide_band)

        self.label = QLabel(band.series.name())

        layout = QHBoxLayout()

        layout.addWidget(self.toggle)
        layout.addWidget(self.color_indicator)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def hide_band(self, checked):
        self.band.setVisible(checked)



class LegendItem(QFrame):

    SELECTED_WIDTH = 11
    NORMAL_WIDTH = 5


    def __init__(self, bands: List[HapiSeries], name, chart):
        QFrame.__init__(self)

        self.chart = chart
        self.bands = bands

        self.band_widgets = []

        def band_hide_function_gen(band):
            def hide(checked):
                band.setVisible(not checked)
            return hide

        for band in self.bands:
            self.band_widgets.append(BandWidget(band))

        self.toggle_all_layout = QHBoxLayout()
        self.toggle_all = QCheckBox()
        self.toggle_all.setChecked(True)

        def on_toggle_all_toggled(checked: bool):
            for band_widget in self.band_widgets:
                band_widget.toggle.setChecked(checked)

        self.toggle_all.toggled.connect(on_toggle_all_toggled)

        self.label = QLabel('table: {}'.format(name))
        self.label.setWordWrap(True)
        self.toggle_all_layout.addWidget(self.toggle_all)
        self.toggle_all_layout.addWidget(self.label)

        self.layout = QVBoxLayout()

        self.layout.addLayout(self.toggle_all_layout)

        for band_item in self.band_widgets:
            self.layout.addWidget(band_item)

        self.setLayout(self.layout)

        self.on_hover_fn = lambda: ()

        # self.installEventFilter(self)
        self.setMouseTracking(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            band = obj.band
            band.series.setMarkerSize(LegendItem.SELECTED_WIDTH)
            # pen = band.pen()
            # pen.setWidth(LegendItem.SELECTED_WIDTH)
            # band.setPen(pen)
            band.setVisible(not band.isVisible())
            band.setVisible(not band.isVisible())
            return True
        elif event.type() == QEvent.Leave:
            band = obj.band
            band.series.setMarkerSize(LegendItem.NORMAL_WIDTH)
            # pen = band.pen()
            # pen.setWidth(LegendItem.NORMAL_WIDTH)
            # band.setPen(pen)
            band.setVisible(not band.isVisible())
            band.setVisible(not band.isVisible())
            return True
        return False

    def set_on_hover(self, on_hover_fn):
        self.on_hover_fn = on_hover_fn


class BandLegend(QWidget):

    def __init__(self, chart: QChart):
        QWidget.__init__(self)

        self.setWindowTitle("Band Legend")

        self.scroll_area = QScrollArea()
        self.scroll_area.setLayout(QVBoxLayout())
        self.scroll_area.setWidgetResizable(True)
        self.widget = QWidget()
        self.scroll_area.setWidget(self.widget)
        self.widget.setLayout(QVBoxLayout())
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.chart = chart
        self.layout.addWidget(self.scroll_area)
        self.setMouseTracking(True)


    def add_item(self, bands, name):
        self.widget.layout().addWidget(LegendItem(bands, name, self.chart))


