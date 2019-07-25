from PyQt5 import uic
from PyQt5.QtWidgets import *
from metadata.config import Config
import sys

from PyQt5 import QtCore, QtWidgets

from utils.log import TextReceiver
from windows.main_window import MainWindow
from worker.hapi_thread import HapiThread
from worker.hapi_worker import HapiWorker
from worker.work_request import WorkRequest

class ErrorMsgWidget(QWidget):

    def __init__(self, error_string: str, connected: bool):
        QWidget.__init__(self)

        if connected:
            self.setLayout(QHBoxLayout())
            self.layout().addWidget(QLabel(error_string))
            self.error_string = error_string
            self.show()

        self.continue_offline_button: QPushButton = None

        uic.loadUi('layouts/offline.ui', self)

        self.continue_offline_button.clicked.connect(self.__continue_offline_clicked)

        self.show()

    def __continue_offline_clicked(self):
        Config.continue_offline = True

        #Taken from app.run() after the internet check
        from metadata.molecule_meta import MoleculeMeta

        WorkRequest.start_work_process()

        # Hapi is now started automatically in the work process
        # start = HapiWorker(WorkRequest.START_HAPI, {})
        # start.start() # When a start_hapi request is sent, it starts automatically.

        _ = MoleculeMeta(0)
        from metadata.xsc_meta import CrossSectionMeta

        # If the cache is expired, download a list of the cross section meta file.
        # This also populates the CrossSectionMeta.molecule_metas field.
        _ = CrossSectionMeta(0)

        app = QtWidgets.QApplication(sys.argv)

        window = MainWindow()
        window.gui.adjustSize()

        TextReceiver.init(window)

        _qt_result = app.exec_()

        TextReceiver.redirect_close()
        close = HapiWorker(WorkRequest.END_WORK_PROCESS, {}, callback=None)
        close.safe_exit()
        WorkRequest.WORKER.process.join()
        HapiThread.kill_all()