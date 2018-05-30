import sys
import threading
from time import sleep

sources = {
    'hapi': {
        'authors': ['R.V. Kochanov', 'I.E. Gordon', 'L.S. Rothman', 'P. Wcislo', 'C. Hill','J.S. Wilzewski'],
        'title': 'HITRAN Application Programming Interface (HAPI): A comprehensive approach to working with spectroscopic data',
        'year': '2016',
        'doi': '10.1016/j.jqsrt.2016.03.005'
    },
    'hapiest': {
        'authors': ['W. Matt', 'J. Karns', 'B. Cairo', 'M. Sova', 'E. Messer', 'D. Lohmann', 'R.V. Kochanov',
                    'I.E. Gordon', 'B. Tenbergen', 'S. Kanbur'],
        'title': 'HAPIEST: A GUI for HAPI',
        'year': '2018',
        'doi': None
    }
}

from .test import Test
from PyQt5 import QtGui, QtWidgets, QtCore
from ..widgets.hapi_source_widget import HapiSourceWidget

class HapiSourcesTest(Test):
    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'hapi sources test'
    
    def test(self) -> bool:
        app = QtWidgets.QApplication(sys.argv)
    
        window = QtWidgets.QMainWindow()
        def close_window():
            sleep(0.25)
            window.deleteLater()
            
        t = threading.Thread(target=close_window)
        t.start()
        items = QtWidgets.QWidget(window)
        layout = QtWidgets.QVBoxLayout()
        for k, v in sources.items():
            layout.addWidget(HapiSourceWidget(v['title'], v['authors'], v['year'], v['doi']))
        items.setLayout(layout)
        window.setCentralWidget(items) 
        window.show()
        qt_result = app.exec_()
        return qt_result == 0
