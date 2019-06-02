from typing import List

from PyQt5.QtChart import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame, QScrollArea, QSizePolicy, QSpacerItem, QWidget, QCheckBox, \
    QLabel, QHBoxLayout, QVBoxLayout
from graphing.hapi_series import HapiSeries

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

        self.visibility_toggle = QCheckBox("      ")
        self.visibility_toggle.setChecked(True)
        self.visibility_toggle.toggled.connect(self.hide_band)

        self.bold_toggle = QCheckBox("      ")
        self.bold_toggle.setChecked(False)
        self.bold_toggle.toggled.connect(self.__on_bold_check_toggled)

        self.label = QLabel(band.series.name())

        layout = QHBoxLayout()

        layout.addWidget(self.visibility_toggle)
        layout.addWidget(self.bold_toggle)
        layout.addWidget(self.color_indicator)
        layout.addWidget(self.label)
        layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Maximum))

        self.setLayout(layout)

    def hide_band(self, checked):
        self.band.setVisible(checked)

    def set_bold(self):
        self.band.series.setMarkerSize(LegendItem.SELECTED_WIDTH)

    def set_normal(self):
        self.band.series.setMarkerSize(LegendItem.NORMAL_WIDTH)

    def __on_bold_check_toggled(self, checked):
        if checked:
            self.set_bold()
        else:
            self.set_normal()
        self.band.series.setVisible(not self.band.isVisible())
        self.band.series.setVisible(not self.band.isVisible())


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
        self.toggle_all = QCheckBox("      ")
        self.toggle_all.setChecked(True)
        self.toggle_all_bold = QCheckBox("     ")
        self.toggle_all_bold.setChecked(False)

        def on_toggle_all_toggled(checked: bool):
            for band_widget in self.band_widgets:
                band_widget.visibility_toggle.setChecked(checked)

        def on_toggle_all_bold_toggled(checked: bool):
            for band_widget in self.band_widgets:
                band_widget.bold_toggle.setChecked(checked)

        self.toggle_all.toggled.connect(on_toggle_all_toggled)
        self.toggle_all_bold.toggled.connect(on_toggle_all_bold_toggled)

        self.label = QLabel('table: {}'.format(name))
        self.label.setWordWrap(True)
        self.toggle_all_layout.addWidget(self.toggle_all)
        self.toggle_all_layout.addSpacerItem(
            QSpacerItem(20, 1, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.toggle_all_layout.addWidget(self.toggle_all_bold)
        self.toggle_all_layout.addWidget(self.label)
        self.toggle_all_layout.addSpacerItem(
            QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Maximum))

        self.layout = QVBoxLayout()

        self.layout.addLayout(self.toggle_all_layout)

        for band_item in self.band_widgets:
            self.layout.addWidget(
                band_item)  # The hover-to-bolden feature has been replaced  # 
            # band_item.installEventFilter(self)
        self.layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(self.layout)

        self.on_hover_fn = lambda: ()

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
        self.setWindowIcon(program_icon())

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

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(QLabel("Visible?  "))
        self.hlayout.addWidget(QLabel("Bold?      "))
        self.hlayout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.widget.layout().addLayout(self.hlayout)

    def add_item(self, bands, name):
        self.widget.layout().addWidget(LegendItem(bands, name, self.chart))
