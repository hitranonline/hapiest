from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class HapiChartView(QChartView):

    def __init__(self, graph_display_window_gui):
        QChartView.__init__(self, graph_display_window_gui.chart)
        self.graph_display_window_gui = graph_display_window_gui
        self.mouse_moved = False

    def mouseMoveEvent(self, event):
        self.mouse_moved = True
        QChartView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if not self.mouse_moved and event.button() == Qt.LeftButton:
            self.graph_display_window_gui.on_point_clicked()
        else:
            self.mouse_moved = False
            QChartView.mouseReleaseEvent(self, event)
