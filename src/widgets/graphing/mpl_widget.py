import matplotlib as mp
# This is important - it must occur before other matplotlib imports
# All it does is ensure matplotlib is using the PyQt5 backend
from PyQt5 import QtCore
from matplotlib import axes


mp.use('QT5Agg')

from PyQt5.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QMainWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.ax: axes.SubplotBase = self.fig.add_subplot(111)

        FigureCanvasQTAgg.__init__(self, self.fig)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def show_legend(self):
        self.fig.legend(loc=9)


class MplWidget(QMainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = MplCanvas()
        self.setCentralWidget(self.canvas)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar2QT(self.canvas, self))

    def add_graph(self, x, y, title, titlex, titley, name, args):
        self.canvas.ax.plot(x, y, label=name)
        self.canvas.show_legend()
