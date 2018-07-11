from PyQt5 import QtGui, QtWidgets, uic, QtCore
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.colors import Colors
from utils.hapiest_util import *
from utils.log import *
from utils.graph_type import GraphType
from widgets.gui import GUI
from widgets.view_selector import ViewSelector
from widgets.hapi_chart_view import HapiChartView
from random import randint
from typing import *
from utils.config import Config

import os
import json
import math


class GraphDisplayWindowGui(GUI, QtWidgets.QMainWindow):

    def __init__(self, ty: GraphType, window_title: str):
        QtWidgets.QMainWindow.__init__(self)
        GUI.__init__(self)

        self.graph_ty = ty

        self.colors = Colors()

        self.xmin: float = None
        self.xmax: float = None
        self.ymin: float = None
        self.ymax: float = None

        uic.loadUi('layouts/graph_display_window.ui', self)
        self.chart: QChart = None
        self.chart_view: HapiChartView = None

        self.view_fit.triggered.connect(self.__on_view_fit_triggered)
        self.exact_fit.triggered.connect(self.__on_exact_fit_triggered)

        self.y_log10.triggered.connect(self.__on_y_log10_triggered)
        self.y_ln.triggered.connect(self.__on_y_ln_triggered)
        self.y_linear.triggered.connect(self.__on_y_linear_triggered)

        self.x_log10.triggered.connect(self.__on_x_log10_triggered)
        self.x_ln.triggered.connect(self.__on_x_ln_triggered)
        self.x_linear.triggered.connect(self.__on_x_linear_triggered)

        self.save_as_csv.triggered.connect(self.__on_save_as_csv_triggered)
        self.save_as_json.triggered.connect(self.__on_save_as_json_triggered)
        self.save_as_txt.triggered.connect(self.__on_save_as_txt_triggered)
        self.save_as_png.triggered.connect(self.__on_save_as_png_triggered)
        self.save_as_jpg.triggered.connect(self.__on_save_as_jpg_triggered)
        # self.save_as_other_img.triggered.connect(self.__on_save_as_other_img_triggered)
        self.grabGesture(QtCore.Qt.PanGesture)
        self.grabGesture(QtCore.Qt.PinchGesture)

        self.axisy = None
        self.axisx = None
        self.view_xmin = None
        self.view_xmax = None
        self.view_ymin = None
        self.view_ymax = None
        self.chart = None
        self.highlighted_point = None
        self.series = []
        self.set_chart_title(window_title)

        self.show()

    def all_series(self):
        return self.series

    def set_chart_title(self, title):
        self.setWindowTitle(str(title))

    def set_viewport(self, xmin: float, xmax: float, ymin: float, ymax: float):
        if xmin > xmax:
            t = xmin
            xmin = xmax
            xmax = t
        if ymin > ymax:
            t = ymin
            ymin = ymax
            ymax = t

        self.xmin, self.xmax = (xmin, xmax)
        self.ymin, self.ymax = (ymin, ymax)
        self.axisx.setRange(xmin, xmax)
        self.axisy.setRange(ymin, ymax)

    def add_graph(self, x, y, title, xtitle, ytitle, name, args):
        if self.chart is None:
            series = QLineSeries()
            color_rgb: int = self.colors.next()
            color = QColor(color_rgb)
            pen = QPen()
            pen.setColor(color)
            pen.setWidth(4)
            pen.setCosmetic(False)
            series.setPen(pen)
            for i in range(0, x.size):
                series.append(x[i], y[i])
            self.series = [series]
            series.setName(
                name + ' -<br>Function: {},<br>T: {:.2f} K, P: {:.2f} atm<br>γ-air: {:.2f}, γ-self: {:.2f}'.format(
                    args['graph_fn'], args['Environment']['T'], args['Environment']['p'],
                    args['Diluent']['air'], args['Diluent']['self']))

            series.setUseOpenGL(True)
            self.chart = QChart()
            self.chart.addSeries(series)
            self.chart.setTitle(title)
            # self.chart.legend().setAlignment(QtCore.Qt.AlignRight)

            if self.axisy:
                self.chart.removeAxis(self.axisy)
                self.chart.removeAxis(self.axisx)

            self.axisx = QValueAxis()
            self.axisx.setTickCount(5)
            self.axisx.setTitleText(xtitle)
            self.chart.addAxis(self.axisx, QtCore.Qt.AlignBottom)
            self.series[0].attachAxis(self.axisx)

            self.axisy = QValueAxis()
            self.axisy.setTitleText(ytitle)
            self.axisy.setTickCount(5)
            self.chart.addAxis(self.axisy, QtCore.Qt.AlignLeft)
            self.series[0].attachAxis(self.axisy)

            self.chart.legend()
            self.chart_view = HapiChartView(self)
            self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
            self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

            self.loading_label.setDisabled(True)
            self.graph_container.layout().addWidget(self.chart_view)
            self.graph_container.layout().removeWidget(self.loading_label)
        else:
            series = QLineSeries()

            color_rgb: int = self.colors.next()
            color = QColor(color_rgb)
            pen = QPen()
            pen.setColor(color)
            pen.setWidth(4)
            pen.setCosmetic(False)
            series.setPen(pen)

            series.setName(name + ' -<br>Function={},<br>T={:.2f}, P={:.2f}<br>γ-air: {:.2f}, γ-self: {:.2f}'.format(
                args['graph_fn'], args['Environment']['T'], args['Environment']['p'],
                args['Diluent']['air'], args['Diluent']['self']))
            series.setUseOpenGL(True)
            for i in range(0, x.size):
                series.append(x[i], y[i])
            self.chart.addSeries(series)
            series.attachAxis(self.axisy)
            series.attachAxis(self.axisx)
            self.series.append(series)

        if self.view_xmin:
            if self.view_xmin > x[0]:
                self.view_xmin = x[0]
        else:
            self.view_xmin = self.axisx.min()
        if self.view_ymin:
            ymin = min(y)
            if self.view_ymin > ymin:
                self.view_ymin = ymin
        else:
            self.view_ymin = self.axisy.min()

        if self.view_xmax:
            if self.view_xmax < x[len(x) - 1]:
                self.view_xmax = x[len(x) - 1]
        else:
            self.view_xmax = self.axisx.max()
        if self.view_ymax:
            ymax = max(y)
            if self.view_ymax < ymax:
                self.view_ymax = ymax
        else:
            self.view_ymax = self.axisy.max()
        self.__on_view_fit_triggered(True)

    def on_view_fit_triggered(self, _checked: bool = False):
        self.__on_view_fit_triggered(_checked)

    def __on_view_fit_triggered(self, _checked: bool = False):
        """
        Sets the screen focus to maximum values of y and x for series in the graph. The xmin / ymin variables
        are kept track of in such a way where they will always have the most extreme valid values, so using those
        to define the range works to fit the view

        """
        if self.chart:
            self.axisx.setRange(self.view_xmin, self.view_xmax)
            self.axisy.setRange(self.view_ymin, self.view_ymax)

    def __on_exact_fit_triggered(self):
        self.view_fit_widget = ViewSelector(self)

    def on_point_clicked(self):
        if self.chart == None:
            return

        if self.highlighted_point != None:
            self.chart.removeSeries(self.highlighted_point)

        global_coord = QCursor.pos()
        widget_coord = self.chart_view.mapFromGlobal(global_coord)
        scene_coord = self.chart_view.mapToScene(widget_coord)
        chart_item_coord = self.chart.mapFromScene(scene_coord)
        point = self.chart.mapToValue(chart_item_coord)
        px, py = (point.x(), point.y())

        def dist(p1, p2):
            x1, y1 = (p1.x(), p1.y())
            x2, y2 = (p2.x(), p2.y())
            a = x1 - x2
            a *= a
            b = y1 - y2
            b *= b
            return math.sqrt(a + b)

        x, y = None, None
        min_dist = 100000
        for series in self.series:
            points = series.pointsVector()
            if len(points) <= 1 or px < points[0].x() or px > points[len(points) - 1].x():
                continue
            dx = points[1].x() - points[0].x()
            index = int((px - points[0].x()) // dx)
            np = points[index]
            distance = dist(point, np)
            if distance < min_dist:
                x, y = (np.x(), np.y())
                min_dist = distance
            if index + 1 >= len(points):
                continue
            np = points[index + 1]
            distance = dist(point, np)
            if distance < min_dist:
                x, y = (np.x(), np.y())
                min_dist = distance

        if x == None:
            return

        self.highlighted_point = QScatterSeries()
        self.highlighted_point.append(x, y)
        self.highlighted_point.setName("Selected point:<br>x: {},<br>y: {}".format(x, y))
        color = QColor(0, 0, 0)
        self.chart.addSeries(self.highlighted_point)
        self.highlighted_point.brush().setColor(color)
        self.highlighted_point.pen().setColor(color)
        self.highlighted_point.pen().setWidth(8)
        self.highlighted_point.attachAxis(self.axisx)
        self.highlighted_point.attachAxis(self.axisy)

    def get_file_save_name(self, extension, filter) -> Union[str, None]:
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save as", "./data" + extension, filter)
        if filename[0] == "":
            return None
        else:
            return str(filename[0])

    def __on_save_as_other_img_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name('.png',
                                           'Portable Network Graphics (*.png *.PNG);; Windows Bitmap (*.bmp *.BMP);; Joint Photographic Experts Group (*.jpeg *.JPEG *.jpg *.JPG);; Portable Pixmap (*.ppm *.PPM);; X11 Bitmap (*.xbm *.XBM);; X11 Pixmap (*.xpm *.XPM)')

        if filename == None:
            return

        _filename, file_extension = os.path.splitext(filename)
        extension = file_extension.upper()

        gl_widget = self.chart_view.findChild(QOpenGLWidget)

        # geometry = self.chart_view.geometry()
        pixmap = self.chart_view.grab()
        painter = QPainter(pixmap)
        point = gl_widget.mapToGlobal(QPoint()) - self.chart_view.mapToGlobal(QPoint())
        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        painter.drawImage(point, gl_widget.grabFramebuffer())
        painter.end()

        pixmap.save(filename, extension)

    def __on_save_as_png_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name('.png', 'Portable Network Graphics (*.png *.PNG)')

        if filename == None:
            return

        gl_widget = self.chart_view.findChild(QOpenGLWidget)

        # geometry = self.chart_view.geometry()
        pixmap = self.chart_view.grab()
        painter = QPainter(pixmap)
        point = gl_widget.mapToGlobal(QPoint()) - self.chart_view.mapToGlobal(QPoint())
        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        painter.drawImage(point, gl_widget.grabFramebuffer())
        painter.end()

        pixmap.save(filename, 'PNG')

    def __on_save_as_jpg_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name('.jpg', 'JPEG files (*.jpg *.JPG *.jpeg *.JPEG)')

        if filename == None:
            return

        gl_widget = self.chart_view.findChild(QOpenGLWidget)

        # geometry = self.chart_view.geometry()
        pixmap = self.chart_view.grab()
        painter = QPainter(pixmap)
        point = gl_widget.mapToGlobal(QPoint()) - self.chart_view.mapToGlobal(QPoint())
        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        painter.drawImage(point, gl_widget.grabFramebuffer())
        painter.end()

        pixmap.save(filename, 'JPG')

    def __on_save_as_txt_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name(".txt", "Text files (*.txt)")

        if filename == None:
            return

        try:
            for i in range(0, len(self.series)):
                ith_filename = '{}_{}.txt'.format(filename, i)
                with open(ith_filename, "w") as file:
                    for point in self.series[i].pointsVector():
                        file.write('{:<16.8f}{:.8f}\n'.format(point.x(), point.y()))

        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))

    def __on_save_as_json_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name(".json", "Javascript object notation files (*.json)")
        if filename == None:
            return

        def filter_series_name(s):
            return s.replace('<br>', ' ').replace('γ', 'gamma')

        dict = {}
        series_lists = list(map(lambda series: dict.update({
            filter_series_name(series.name()):
                list(map(lambda point: [point.x(), point.y()], series.pointsVector()))}), self.series))
        try:
            with open(filename, 'w') as file:
                file.write(json.dumps(dict, indent=4))
        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))

    def __on_save_as_csv_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name(".csv", "Comma separated value files (*.csv)")

        if filename == None:
            return

        try:
            point_vectors = []
            for i in range(0, len(self.series)):
                point_vectors.append(self.series[i].pointsVector())
            max_len = max(map(len, point_vectors))
            with open(filename, "w") as file:
                for point_index in range(0, max_len):
                    s = ''
                    for i in range(0, len(self.series)):
                        if point_index >= len(point_vectors[i]):
                            s = '{} {:14s}, {:14s},'.format(s, '', '')
                        else:
                            point = point_vectors[i][point_index]
                            s = '{} {:14s}, {:14s},'.format(s, str(point.x()), str(point.y()))

                    file.write('{}\n'.format(s))

        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))

    def swap_axis(self, old_axis: QAbstractAxis, new_axis: QAbstractAxis, alignment):
        self.chart.addAxis(new_axis, alignment)

        for series in self.all_series():
            series.detachAxis(old_axis)
            self.chart.removeSeries(series)
            self.chart.addSeries(series)
            series.attachAxis(new_axis)

        self.chart.removeAxis(old_axis)

    def __on_y_log10_triggered(self, _checked: bool = False):
        if self.axisy is None:
            return
        new_axisy = QLogValueAxis()
        new_axisy.setTitleText(self.axisy.titleText())
        new_axisy.setBase(10)
        new_axisy.setLabelFormat(self.axisy.labelFormat())

        self.swap_axis(self.axisy, new_axisy, Qt.AlignLeft)
        self.axisy = new_axisy

        self.__on_view_fit_triggered()

    def __on_y_ln_triggered(self, _checked: bool = False):
        if self.axisy == None:
            return

        new_axisy = QLogValueAxis()
        new_axisy.setTitleText(self.axisy.titleText())
        new_axisy.setBase(math.e)
        new_axisy.setLabelFormat(self.axisy.labelFormat())

        self.swap_axis(self.axisy, new_axisy, Qt.AlignLeft)

        self.axisy = new_axisy

        self.__on_view_fit_triggered()

    def __on_y_linear_triggered(self, _checked: bool = False):
        if self.axisy == None:
            return

        new_axisy = QValueAxis()
        new_axisy.setTitleText(self.axisy.titleText())
        new_axisy.setTickCount(Config.axisy_ticks)
        new_axisy.setLabelFormat(self.axisy.labelFormat())

        self.swap_axis(self.axisy, new_axisy, Qt.AlignLeft)

        self.axisy = new_axisy

        self.__on_view_fit_triggered()

    def __on_x_log10_triggered(self, _checked: bool = False):
        if self.axisx == None:
            return

        new_axisx = QLogValueAxis()
        new_axisx.setTitleText(self.axisx.titleText())
        new_axisx.setBase(10.0)
        new_axisx.setLabelFormat(self.axisx.labelFormat())

        self.swap_axis(self.axisx, new_axisx, Qt.AlignBottom)

        self.axisx = new_axisx

        self.__on_view_fit_triggered()

    def __on_x_ln_triggered(self, _checked: bool = False):
        if self.axisx == None:
            return

        new_axisx = QLogValueAxis()
        new_axisx.setTitleText(self.axisx.titleText())
        new_axisx.setBase(math.e)
        new_axisx.setLabelFormat(self.axisx.labelFormat())

        self.swap_axis(self.axisx, new_axisx, Qt.AlignBottom)

        self.axisx = new_axisx

        self.__on_view_fit_triggered()

    def __on_x_linear_triggered(self, _checked: bool = False):
        if self.axisx == None:
            return

        new_axisx = QValueAxis()
        new_axisx.setTitleText(self.axisx.titleText())
        new_axisx.setTickCount(Config.axisx_ticks)
        new_axisx.setLabelFormat(self.axisx.labelFormat())

        self.swap_axis(self.axisx, new_axisx, Qt.AlignBottom)

        self.axisx = new_axisx

        self.__on_view_fit_triggered()
