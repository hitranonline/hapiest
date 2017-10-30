from PyQt5 import QtGui, QtWidgets, uic, QtCore
<<<<<<< HEAD
from util import * #edited src.
=======
from util import *
>>>>>>> origin/master
import multiprocessing
import pickle


class Worker(QtCore.QThread):
    worker_id = 0

    error_signal = QtCore.pyqtSignal(object)
    done_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent, work_function, callback=None, error_callback=None):
        super(Worker, self).__init__()
        self.parent = parent
        self.callback = callback
        self.errors_callback = error_callback
        self.work_function = work_function

        self.started.connect(self.__run)

        def f(x):
            try:
                callback(x)
            except Exception as e:
                debug(str(e))

        if callback:
            self.done_signal.connect(lambda x: callback(x))
        if error_callback:
            self.error_signal.connect(lambda x: error_callback(x))

        self.work_function = work_function
        self.errors = []

    def __run(self):
        errors = []
        try:
            result = self.work_function(errors)
            self.done_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(errors)
