from PyQt5 import QtGui, QtWidgets, uic, QtCore


class Window(QtCore.QObject):
    @staticmethod
    def start(window):
        QtCore.QCoreApplication.postEvent(window, QtCore.QEvent)

    def __init__(self, widget):
        self.widget = widget

    def event(self, e):
        if e.type() == QtCore.QEvent.User:
            self.widget.show()
            return True
        return False
