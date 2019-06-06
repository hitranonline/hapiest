import json
import math
from typing import *

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtChart import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QOpenGLWidget, QLabel, QMainWindow

from graphing.graph_type import GraphType
from graphing.hapi_series import HapiSeries
from utils.colors import Colors
from utils.hapiest_util import *
from utils.log import *
from widgets.graphing.hapi_chart_view import HapiChartView
from widgets.graphing.view_selector import ViewSelector
from worker.hapi_worker import HapiWorker, WorkResult
from worker.work_request import WorkRequest


class GraphDisplayWidget(QMainWindow):
    done_signal = QtCore.pyqtSignal(object)

    graph_ty_to_work_ty = {
            GraphType.ABSORPTION_COEFFICIENT:   WorkRequest.ABSORPTION_COEFFICIENT,
            GraphType.TRANSMITTANCE_SPECTRUM:   WorkRequest.TRANSMITTANCE_SPECTRUM,
            GraphType.RADIANCE_SPECTRUM:        WorkRequest.RADIANCE_SPECTRUM,
            GraphType.ABSORPTION_SPECTRUM:      WorkRequest.ABSORPTION_SPECTRUM,
            GraphType.BANDS:                    WorkRequest.BANDS
        }

    graph_windows = {}

    next_graph_graph_display_id = 1

    @staticmethod
    def graph_display_id():
        r = GraphDisplayWidget.next_graph_graph_display_id
        GraphDisplayWidget.next_graph_graph_display_id += 1
        return r

    @staticmethod
    def remove_child_window(graph_display_id: int):
        from widgets.graphing.graphing_widget import GraphingWidget

        if graph_display_id in GraphDisplayWidget.graph_windows:
            print(GraphDisplayWidget.graph_windows.pop(graph_display_id))
        GraphingWidget.GRAPHING_WIDGET_INSTANCE.update_existing_window_items()

    def __init__(self, graph_ty: GraphType, work_object: Dict):
        """
        Initializes the GUI and sends a work request for the graph to be plotted, and connect
        signals to the appropriate handler methods.

        :param ty the type of graph to be calculated. May be different for different types of graphs
        :param work_object has information about the graph that is to be made
        :param parent the parent QObject

        """
        QMainWindow.__init__(self)

        self.graph_ty = graph_ty
        self.graph_display_id = GraphDisplayWidget.graph_display_id()
        self.workers = {
            0: HapiWorker(GraphDisplayWidget.graph_ty_to_work_ty[graph_ty], work_object,
                          lambda x: (self.plot(x), self.workers.pop(0)))
            }

        GraphDisplayWidget.graph_windows[self.graph_display_id] = self

        self.workers[0].start()
        self.cur_work_id = 1

        from widgets.graphing.graphing_widget import GraphingWidget

        self.done_signal.connect(lambda: GraphingWidget.GRAPHING_WIDGET_INSTANCE.done_graphing())
        self.setWindowTitle(f"{work_object['title']} - {str(self.graph_display_id)}")

        self.setWindowIcon(program_icon())

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
        self.set_chart_title(self.windowTitle())

        self.axisx_type = "linear"
        self.axisy_type = "linear"

        self.point_label: QLabel = QLabel()

        self.show()

    def add_worker(self, graph_ty, work_object):
        id = self.cur_work_id
        self.cur_work_id += 1
        worker = HapiWorker(GraphDisplayWidget.graph_ty_to_work_ty[graph_ty], work_object,
                            lambda x: (self.plot(x), self.workers.pop(id)))

        self.workers[id] = worker
        worker.start()


    def closeEvent(self, event):
        self.close()
        event.accept()

    def reject(self):
        self.close()

    def close(self):
        """
        Overrides Window.close implementation, removes self from GraphDisplayWindow.graph_windows
        """
        from widgets.graphing.graphing_widget import GraphingWidget

        GraphDisplayWidget.graph_windows.pop(self.graph_display_id, None)
        GraphingWidget.GRAPHING_WIDGET_INSTANCE.update_existing_window_items()
        QMainWindow.close(self)

    def plot(self, work_result: WorkResult):
        """
        Plots the graph stored in 'work_result', which may be an error message rather than a result
        dictionary. If this is the case the error is printed to the console. This also emits a
        'done' signal.

        :param work_result the result of the HapiWorker; it will either be a string (which
        indicates an error), or it
                            will be a dictionary that contains the x and y coordinates and some
                            information about graph
                            labels
        """
        self.done_signal.emit(0)

        if type(work_result.result) != dict:
            err_log('Encountered error while graphing: ' + str(work_result.result))
            return

        try:
            result = work_result.result
            (x, y) = result['x'], result['y']
            self.add_graph(x, y, result['title'], result['titlex'], result['titley'],
                               result['name'], result['args'])
        except Exception as e:
            err_log(e)

    def __on_close_fn(self):
        GraphDisplayWidget.remove_child_window(self.graph_display_id)

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
            if 'xsc' in args and args['xsc']:
                series.setName(name)
            else:
                series.setName(
                    name + ' -<br>Function: {},<br>T: {:.2f} K, P: {:.2f} atm<br>air: {:.2f}, '
                           'self: {:.2f}'.format(args['graph_fn'], args['Environment']['T'],
                            args['Environment']['p'], args['Diluent']['air'], args['Diluent']['self']))

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
            if 'xsc' in args and args['xsc']:
                series.setName(name)
            else:
                series.setName(name + ' -<br>Function={},<br>T={:.2f}, P={:.2f}<br>air: {:.2f}, '
                                      'self: {:.2f}'.format(args['graph_fn'],
                    args['Environment']['T'], args['Environment']['p'], args['Diluent']['air'],
                    args['Diluent']['self']))
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
        Sets the screen focus to maximum values of y and x for series in the graph. The xmin /
        ymin variables
        are kept track of in such a way where they will always have the most extreme valid
        values, so using those
        to define the range works to fit the view

        """
        if self.chart:
            self.axisx.setRange(self.view_xmin, self.view_xmax)
            self.axisy.setRange(self.view_ymin, self.view_ymax)

    def __on_exact_fit_triggered(self):
        self.view_fit_widget = ViewSelector(self)

    def on_point_clicked(self):
        if self.chart is None:
            return

        if self.highlighted_point is not None:
            self.chart.removeSeries(self.highlighted_point.series)

        # Adding a new series seems to change the viewport as determined by axes, so the viewport
        # must be recorded and then restored after the series has been added
        minx, maxx = self.axisx.min(), self.axisx.max()
        miny, maxy = self.axisy.min(), self.axisy.max()

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

        if x is None:
            return

        self.highlighted_point = HapiSeries()
        self.highlighted_point.add_to_chart(self.chart)
        self.highlighted_point.append(x, y)
        self.highlighted_point.setName(self.point_label.text())
        color = QColor(0, 0, 0)
        self.highlighted_point.brush().setColor(color)
        self.highlighted_point.pen().setColor(color)
        self.highlighted_point.pen().setWidth(8)
        self.highlighted_point.attachAxis(self.axisx)
        self.highlighted_point.attachAxis(self.axisy)

        self.axisx.setMax(maxx)
        self.axisx.setMin(minx)

        self.axisy.setMax(maxy)
        self.axisy.setMin(miny)

    def get_file_save_name(self, extension, file_filter) -> Union[str, None]:
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save as", "./data" + extension,
                                                         file_filter)
        if filename[0] == "":
            return None
        else:
            return str(filename[0])

    def __on_save_as_other_img_triggered(self, _checked: bool):
        if self.chart is None:
            return

        filename = self.get_file_save_name('.png',
                                           'Portable Network Graphics (*.png *.PNG);; Windows '
                                           'Bitmap (*.bmp *.BMP);; Joint Photographic Experts '
                                           'Group (*.jpeg *.JPEG *.jpg *.JPG);; Portable Pixmap ('
                                           '*.ppm *.PPM);; X11 Bitmap (*.xbm *.XBM);; X11 Pixmap '
                                           '(*.xpm *.XPM)')

        if filename is None:
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
        if self.chart is None:
            return

        filename = self.get_file_save_name('.png', 'Portable Network Graphics (*.png *.PNG)')

        if filename is None:
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
        if self.chart is None:
            return

        filename = self.get_file_save_name('.jpg', 'JPEG files (*.jpg *.JPG *.jpeg *.JPEG)')

        if filename is None:
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
        if self.chart is None:
            return

        filename = self.get_file_save_name(".txt", "Text files (*.txt)")

        if filename is None:
            return

        try:
            i = 0
            if len(self.all_series()) == 0:
                with open(filename, "w") as file:
                    series = self.all_series()[0]
                    for point in series.pointsVector():
                        file.write('{:<16.8e}{:.8e}\n'.format(point.x(), point.y()))
                return

            for series in self.all_series():
                ith_filename = '{} {}.txt'.format(filename[0:len(filename) - 4], series.name())
                with open(ith_filename, "w") as file:
                    for point in series.pointsVector():
                        file.write('{:<16.8e}{:.8e}\n'.format(point.x(), point.y()))
                i += 1
        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))

    def __on_save_as_json_triggered(self, _checked: bool):
        if self.chart is None:
            return

        filename = self.get_file_save_name(".json", "Javascript object notation files (*.json)")
        if filename is None:
            return

        def to_x_y_arrays(series):
            points_vector = series.pointsVector()
            x = []
            y = []
            for point in points_vector:
                x.append(point.x())
                y.append(point.y())
            return {'x': x, 'y': y}

        dic = {}
        series_lists = list(map(lambda series: dic.update({series.name(): to_x_y_arrays(series)}),
                                self.all_series()))
        try:
            with open(filename, 'w') as file:
                file.write(json.dumps(dic, indent=4))
        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))

    def __on_save_as_csv_triggered(self, _checked: bool):
        if self.chart is None:
            return

        filename = self.get_file_save_name(".csv", "Comma separated value files (*.csv)")

        if filename is None:
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
        if self.axisy is None:
            return

        self.axisy_type = "ln"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_y_linear_triggered(self, _checked: bool = False):
        if self.axisy is None:
            return

        self.axisy_type = "linear"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_x_log10_triggered(self, _checked: bool = False):
        if self.axisx is None:
            return

        self.axisx_type = "log10"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_x_ln_triggered(self, _checked: bool = False):
        if self.axisx is None:
            return

        self.axisx_type = "ln"
        self.swap_axis()

        self.__on_view_fit_triggered()

    def __on_x_linear_triggered(self, _checked: bool = False):
        if self.axisx is None:
            return

        self.axisx_type = "linear"
        self.swap_axis()

        self.__on_view_fit_triggered()
