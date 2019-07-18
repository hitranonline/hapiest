from typing import List, Dict

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame, QScrollArea, QSizePolicy, QSpacerItem, QWidget, QCheckBox, \
    QLabel, QHBoxLayout, QVBoxLayout
from matplotlib.lines import Line2D
import matplotlib.colors as mpc

from data_structures.bands import Bands

from utils.hapiest_util import *


class BandWidget(QWidget):

    def __init__(self, line: Line2D, name: str, parent):
        QWidget.__init__(self, parent)

        self.parent = parent
        self.line = line
        self.name = name

        self.color_indicator = QWidget()
        self.color_indicator.setFixedSize(24, 24)
        self.enterEvent(None)  # This sets the color

        self.visibility_toggle = QCheckBox("      ")
        self.visibility_toggle.setChecked(True)
        self.visibility_toggle.toggled.connect(self.__on_visible_check_toggled)

        self.bold_toggle = QCheckBox("      ")
        self.bold_toggle.toggled.connect(self.__on_bold_check_toggled)
        self.bold_toggle.setChecked(False)

        self.label = QLabel(self.name)

        layout = QHBoxLayout()

        layout.addWidget(self.visibility_toggle)
        layout.addWidget(self.bold_toggle)
        layout.addWidget(self.color_indicator)
        layout.addWidget(self.label)
        layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Maximum))

        self.setLayout(layout)

    def enterEvent(self, event):
        # Recalculate style every time there is a hover, since the colors can be changed through
        # the matplotlib gui
        # This string has a '#' at the beginning of it
        color_hex_str = mpc.rgb2hex(mpc.ColorConverter.to_rgb(self.line.get_color()))
        style = """
        QWidget {{
            background-color: {};
            border: 1px solid black;
        }}
        """.format(color_hex_str)
        self.color_indicator.setStyleSheet(style)

    def __on_visible_check_toggled(self, checked):
        self.line.set_visible(checked)
        self.parent.update_plot()

    def set_width(self, width):
        self.line.set_markersize(width)
        self.parent.update_plot()

    def __on_bold_check_toggled(self, checked):
        if checked:
            self.set_width(LegendItem.SELECTED_WIDTH)
        else:
            self.set_width(LegendItem.NORMAL_WIDTH)
        self.parent.update_plot()


class LegendItem(QFrame):
    SELECTED_WIDTH = 11
    NORMAL_WIDTH = 5

    def __init__(self, bands: Dict[str, Line2D], table_name: str, legend: 'BandLegend'):
        QFrame.__init__(self)

        self.should_update = True

        self.table_name = table_name
        self.legend = legend
        self.bands = bands

        self.band_widgets = []

        for band_name in self.bands:
            self.band_widgets.append(BandWidget(bands[band_name], band_name, self))

        self.toggle_all_layout = QHBoxLayout()
        self.toggle_all = QCheckBox("      ")
        self.toggle_all.setChecked(True)
        self.toggle_all_bold = QCheckBox("     ")
        self.toggle_all_bold.setChecked(False)

        def on_toggle_all_toggled(checked: bool):
            self.should_update = False
            for band_widget in self.band_widgets:
                band_widget.visibility_toggle.setChecked(checked)
            self.should_update = True
            self.update_plot()

        def on_toggle_all_bold_toggled(checked: bool):
            self.should_update = False
            for band_widget in self.band_widgets:
                band_widget.bold_toggle.setChecked(checked)
            self.should_update = True
            self.update_plot()

        self.toggle_all.toggled.connect(on_toggle_all_toggled)
        self.toggle_all_bold.toggled.connect(on_toggle_all_bold_toggled)

        self.label = QLabel('table: {}'.format(self.table_name))
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
            self.layout.addWidget(band_item)

        self.layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(self.layout)

        self.on_hover_fn = lambda: ()

        self.setMouseTracking(True)

    def set_on_hover(self, on_hover_fn):
        self.on_hover_fn = on_hover_fn

    def update_plot(self):
        if self.should_update:
            self.legend.update_plot()

class BandLegend(QWidget):

    def __init__(self, band_display_widget: 'BandDisplayWidget'):
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
        self.band_display_widget = band_display_widget
        self.layout.addWidget(self.scroll_area)
        self.setMouseTracking(True)

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(QLabel("Visible?  "))
        self.hlayout.addWidget(QLabel("Bold?      "))
        self.hlayout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.widget.layout().addLayout(self.hlayout)

    def add_bands(self, bands: Dict[str, Line2D], table_name: str):
        """
        Add a set of bands for a specific line list
        """
        self.widget.layout().addWidget(LegendItem(bands, table_name, self))

    def update_plot(self):
        self.band_display_widget.update_plot()
