# import vispy
# import vispy as vp
from PyQt5.QtWidgets import QWidget, QHBoxLayout
# from vispy.app import Canvas
# from vispy.plot import Fig, PlotWidget


# vp.use("PyQt5", "gl2")

from widgets.graphing.graph_display_backend import GraphDisplayBackend

# class VispyCanvas(vispy.app.Canvas):
class VispyCanvas:
    def __init__(self):
        """

        vispy.app.Canvas.__init__(self)

        self.transform = vispy.visuals.transforms.TransformSystem(self)

        self.lines = []

        mx = self.margin_x()
        my = self.margin_y()
        px, py = self.physical_size
        self.axis_x = vispy.visuals.AxisVisual((
            (mx, py - my),
            (px - mx, py - my)))
        self.axis_y = vispy.visuals.AxisVisual((
            (mx, py - my),
            (mx, my)))
        """
        pass

    def graph_size(self):
        """
        sx = self.physical_size[0]
        sy = self.physical_size[1]
        return sx * 0.9, sy * 0.9
        """
        pass

    def margin_x(self):
        return self.physical_size[0] * 0.1 / 2

    def margin_y(self):
        return self.physical_size[1] * 0.1 / 2

    def on_draw(self, _event):
        """
        vispy.gloo.clear('black')
        self.axis_x.draw()
        self.axis_y.draw()

        for line in self.lines:
            line.draw()
        """
        pass
    def on_resize(self, _event):
        """
        vp = (0, 0, *self.physical_size)
        self.context.set_viewport(vp)
        self.axis_x.transforms.configure(canvas=self, viewport=vp)
        self.axis_y.transforms.configure(canvas=self, viewport=vp)
        for line in self.lines:
            line.transforms.configure(canvas=self, viewport=vp)
        """
        pass


class VispyWidget(QWidget):

    def __init__(self, parent=None):
        """
        QWidget.__init__(self, parent)
        GraphDisplayBackend.__init__(self)

        self.canvas: VispyCanvas = VispyCanvas()

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.canvas.native)
        self.setLayout(self.layout)
        """
        pass

    def add_graph(self, x, y, title, titlex, titley, name, args):
        """
        line = vispy.visuals.LinePlotVisual((x, y))
        self.canvas.lines.append(line)
        self.canvas.on_draw(None)
        """
        pass

