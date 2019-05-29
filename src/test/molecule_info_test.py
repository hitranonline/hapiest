import threading
from time import sleep


sources = {
    'hapi':    {
        'authors': ['R.V. Kochanov', 'I.E. Gordon', 'L.S. Rothman', 'P. Wcislo', 'C. Hill',
                    'J.S. Wilzewski'],
        'title':   'HITRAN Application Programming Interface (HAPI): A comprehensive approach to '
                   'working with spectroscopic data',
        'year':    '2016',
        'doi':     '10.1016/j.jqsrt.2016.03.005'
        },
    'hapiest': {
        'authors': ['W. Matt', 'J. Karns', 'B. Cairo', 'M. Sova', 'E. Messer', 'D. Lohmann',
                    'R.V. Kochanov',
                    'I.E. Gordon', 'B. Tenbergen', 'S. Kanbur'],
        'title':   'HAPIEST: A GUI for HAPI',
        'year':    '2018',
        'doi':     None
        }
    }

from test.test import Test
from PyQt5 import QtWidgets
from widgets.molecule_info_widget import MoleculeInfoWidget
from metadata.molecule_meta import MoleculeMeta


class MoleculeInfoTest(Test):
    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'molecule view test'

    def test(self) -> bool:
        app = QtWidgets.QApplication([])
        window = QtWidgets.QMainWindow()

        def close_window():
            sleep(0.25)
            window.deleteLater()

        # Necessary initialization
        _ = MoleculeMeta(0)

        t = threading.Thread(target = close_window)
        t.start()
        widget = MoleculeInfoWidget('CO2')
        window.setCentralWidget(widget)
        window.show()
        return app.exec_() == 0
