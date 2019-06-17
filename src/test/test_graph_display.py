import unittest
import math
import random
import threading
from time import sleep
from PyQt5 import QtWidgets
from src.widgets.graphing.graph_display_window_gui import GraphDisplayWindowGui


class TestGraphDisplay(unittest.TestCase):

    def test_graph_display(self):
        app = QtWidgets.QApplication([])
        window = QtWidgets.QMainWindow()

        def close_window():
            sleep(0.25)
            window.deleteLater()

        step = 0.1

        x = list(map(lambda x: float(x) * step, range(0, int(100.0 / step))))

        def random_graph():
            freq = float(random.randint(1, 10)) / 300
            amp = float(random.randint(1, 40))
            y = [0.0] * len(x)
            for i in range(0, int(100.0 / step)):
                y[i] = amp * math.sin(freq * x[i])
            return (x, y)

        t = threading.Thread(target=close_window)
        t.start()
        widget = GraphDisplayWindowGui('a', 1, 'h')
        widget.setMinimumSize(256, 256)
        # def add_graph(self, x, y, title, xtitle, ytitle, name, args):
        args = {'Diluent': {'self': 1.0, 'air': 0.0}, 'graph_fn': '',
                'Environment': {'T': 1, 'p': 0}}
        x, y = random_graph()
        widget.add_graph(x, y, '1', 'x', 'y', 'oof', args)
        x, y = random_graph()
        widget.add_graph(x, y, '2', 'x', 'y', 'oof2', args)
        window.setCentralWidget(widget)
        window.show()
        self.assertEqual(app.exec_(), 0)

if __name__ == '__main__':
    unittest.main()
