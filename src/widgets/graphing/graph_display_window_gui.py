import json
import math
import os
from typing import *

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtChart import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QOpenGLWidget

from utils.graphics.colors import Colors
from utils.graphing.graph_type import GraphType
from utils.graphing.hapi_series import HapiSeries
from utils.hapiest_util import *
from utils.log import *
from utils.metadata.config import Config
from widgets.graphing.hapi_chart_view import HapiChartView
from widgets.graphing.view_selector import ViewSelector
from widgets.gui import GUI


class GraphDisplayWindowGui(GUI, QtWidgets.QMainWindow):

    def __init__(self, ty: GraphType, window_title: str):
        QtWidgets.QMainWindow.__init__(self)
        GUI.__init__(self)

        self.setWindowIcon(program_icon())

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

        self.axisx_type = "linear"
        self.axisy_type = "linear"

        self.point_label: QLabel = QLabel()

        self.show()

    def all_series(self):
        if self.highlighted_point is None:
            return self.series
        else:
            return self.series + [self.highlighted_point]

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
            series = HapiSeries(x, y, False)
            color_rgb: int = self.colors.next()
            color = QColor(color_rgb)
            pen = QPen()
            pen.setColor(color)
            pen.setWidth(4)
            pen.setCosmetic(False)
            series.setPen(pen)

            self.series = [series]
            series.setName(
                name + ' -<br>Function: {},<br>T: {:.2f} K, P: {:.2f} atm<br>γ-air: {:.2f}, γ-self: {:.2f}'.format(
                    args['graph_fn'], args['Environment']['T'], args['Environment']['p'],
                    args['Diluent']['air'], args['Diluent']['self']))

            series.setUseOpenGL(True)
            self.chart = QChart()
            series.add_to_chart(self.chart)
            self.chart.setTitle(title)
            # self.chart.legend().setAlignment(QtCore.Qt.AlignRight)

            if self.axisy:
                self.chart.removeAxis(self.axisy)
                self.chart.removeAxis(self.axisx)

            self.axisx = QValueAxis()
            self.axisx.setTickCount(Config.axisx_ticks)
            self.axisx.setTitleText(xtitle)
            self.chart.addAxis(self.axisx, QtCore.Qt.AlignBottom)
            self.axisx.setLabelFormat(Config.axisx_label_format)
            self.series[0].attachAxis(self.axisx)

            self.axisy = QValueAxis()
            self.axisy.setTitleText(ytitle)
            self.axisy.setTickCount(Config.axisy_ticks)
            self.chart.addAxis(self.axisy, QtCore.Qt.AlignLeft)
            self.axisy.setLabelFormat(Config.axisy_label_format)
            self.series[0].attachAxis(self.axisy)

            self.chart.legend()
            self.chart_view = HapiChartView(self)
            self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
            self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

            self.loading_label.setDisabled(True)
            self.graph_container.layout().addWidget(self.chart_view)
            self.graph_container.layout().addWidget(self.point_label)
            self.graph_container.layout().removeWidget(self.loading_label)
        else:
            series = HapiSeries(x, y, False)

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

            series.add_to_chart(self.chart)
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
            self.chart.removeSeries(self.highlighted_point.series)

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
        for series in self.all_series():
            points = series.pointsVector()
            if len(points) <= 3 or px < points[0].x() or px > points[len(points) - 1].x():
                continue
            dx = series.step
            index = int((px - points[0].x()) / dx)
            np = points[index]
            distance = dist(point, np)
            if distance < min_dist:
                x, y = (np.x(), np.y())
                min_dist = distance
            if index >= len(points):
                continue
            np = points[index + 1]
            distance = dist(point, np)
            if distance < min_dist:
                x, y = (np.x(), np.y())
                min_dist = distance

        if x == None:
            return

        self.highlighted_point = HapiSeries()
        self.highlighted_point.append(x, y)
        self.point_label.setText("Selected point:<br>x: {},<br>y: {}".format(x, y))
        self.highlighted_point.setName(self.point_label.text())
        color = QColor(0, 0, 0)
        self.highlighted_point.add_to_chart(self.chart)
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
            i = 0
            for series in self.all_series():
                print(series.name())
                ith_filename = '{} {}.txt'.format(filename[0:len(filename) - 4], series.name())
                with open(ith_filename, "w") as file:
                    for point in series.pointsVector():
                        file.write('{:<16.8f}{:.8f}\n'.format(point.x(), point.y()))
                i += 1
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
                list(map(lambda point: [point.x(), point.y()], series.pointsVector()))}), self.all_series()))
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
            all_series = self.all_series()
            for series in all_series:
                point_vectors.append(series.pointsVector())
            max_len = max(map(len, point_vectors))
            with open(filename, "w") as file:
                s = ''
                for series in all_series:
                    s += ' {:24s}, {:4s},'.format(series.name(), '')
                file.write('{}\n'.format(s))

                for point_index in range(0, max_len):
                    s = ''
                    for i in range(0, len(point_vectors)):
                        if point_index >= len(point_vectors[i]):
                            s = '{} {:14s}, {:14s},'.format(s, '', '')
                        else:
                            point = point_vectors[i][point_index]
                            s = '{} {:14s}, {:14s},'.format(s, str(point.x()), str(point.y()))

                    file.write('{}\n'.format(s))

        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))

    def make_axis(self):
        if self.axisx_type == "linear":
            axisx = QValueAxis()
            axisx.setTitleText(self.axisx.titleText())
            axisx.setTickCount(Config.axisx_ticks)
            axisx.setLabelFormat(Config.axisx_label_format)
        elif self.axisx_type == "ln":
            axisx = QLogValueAxis()
            axisx.setBase(math.e)
            axisx.setTitleText(self.axisx.titleText())
            axisx.setLabelFormat(Config.axisx_log_label_format)
        else:
            axisx = QLogValueAxis()
            axisx.setBase(10.0)
            axisx.setTitleText(self.axisx.titleText())
            axisx.setLabelFormat(Config.axisx_log_label_format)

        if self.axisy_type == "linear":
            axisy = QValueAxis()
            axisy.setTitleText(self.axisy.titleText())
            axisy.setTickCount(Config.axisy_ticks)
            axisy.setLabelFormat(Config.axisy_label_format)
        elif self.axisy_type == "ln":
            axisy = QLogValueAxis()
            axisy.setBase(math.e)
            axisy.setTitleText(self.axisy.titleText())
            axisy.setLabelFormat(Config.axisy_log_label_format)
        else:
            axisy = QLogValueAxis()
            axisy.setBase(10.0)
            axisy.setTitleText(self.axisy.titleText())
            axisy.setLabelFormat(Config.axisy_log_label_format)

        return axisx, axisy

    def swap_axis(self):
        new_xaxis, new_yaxis = self.make_axis()

        self.chart.removeAxis(self.axisx)
        self.chart.removeAxis(self.axisy)

        self.axisy = new_yaxis
        self.axisx = new_xaxis

        self.chart.addAxis(self.axisx, Qt.AlignBottom)
        self.chart.addAxis(self.axisy, Qt.AlignLeft)

        all_series = self.all_series()

        list(map(lambda s: s.attachAxis(new_yaxis), all_series))

        list(map(lambda s: s.attachAxis(new_xaxis), all_series))

    def __on_y_log10_triggered(self, _checked: bool = False):
        if self.axisy is None:
            return

        self.axisy_type = "log10"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_y_ln_triggered(self, _checked: bool = False):
        if self.axisy == None:
            return

        self.axisy_type = "ln"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_y_linear_triggered(self, _checked: bool = False):
        if self.axisy == None:
            return

        self.axisy_type = "linear"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_x_log10_triggered(self, _checked: bool = False):
        if self.axisx == None:
            return

        self.axisx_type = "log10"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_x_ln_triggered(self, _checked: bool = False):
        if self.axisx == None:
            return

        self.axisx_type = "ln"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_x_linear_triggered(self, _checked: bool = False):
        if self.axisx == None:
            return

        self.axisx_type = "linear"
        self.swap_axis()

        self.__on_view_fit_triggered()
