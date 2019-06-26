import matplotlib as mp
# This is important - it must occur before other matplotlib imports
# All it does is ensure matplotlib is using the PyQt5 backend
from PyQt5 import QtCore
from matplotlib import axes

from widgets.graphing.band_legend import LegendItem
from widgets.graphing.graph_display_backend import GraphDisplayBackend

mp.use('QT5Agg')

from PyQt5.QtWidgets import QWidget, QSizePolicy, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self):
        #if Config.high_dpi:
        #    self.fig = Figure(dpi=100)
        #else:
        self.fig = Figure()
        self.ax: axes.SubplotBase = self.fig.add_subplot(111)

        FigureCanvasQTAgg.__init__(self, self.fig)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def show_legend(self):
        self.fig.legend(loc=9)

    def hide_legend(self):
        self.fig.legends = []

class MplWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        GraphDisplayBackend.__init__(self)

        self.canvas = MplCanvas()
        self.parent().addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar2QT(self.canvas, self))
        print("?")
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def add_graph(self, x, y, title, titlex, titley, name, args):
        self.canvas.ax.plot(x, y, label=name)
        self.canvas.show_legend()
        self.canvas.ax.set_xlabel(titlex)
        self.canvas.ax.set_ylabel(titley)
        self.canvas.draw()

    def hide_legend(self):
        self.canvas.hide_legend()

    def update_canvas(self):
        self.canvas.draw()
        self.canvas.flush_events()

    def add_band(self, x, y):
        return self.canvas.ax.plot(x, y, linewidth=0,
                                   markersize=LegendItem.NORMAL_WIDTH,
                                   marker='o')[0]  # For some reason this returns a list
