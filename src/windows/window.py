from PyQt5 import QtGui, QtWidgets, uic, QtCore
from typing import List
from widgets.gui import GUI

class Window(QtCore.QObject):
    close_signal = QtCore.pyqtSignal(object)

    def __init__(self, gui: GUI, parent: 'Window'):
        super(Window, self).__init__()

        self.parent: Window = parent
        self.gui: GUI = gui
        self.child_windows: List[Window] = []
        self.open = False
        

        self.close_signal.connect(remove_child_window)
        self.gui.set_on_close(lambda: self.close_signal.emit(self))

    
    #def event(self, e):
    #    if e.type() == QtCore.QEvent.User:
    #        self.widget.show()
    #        return True
    #    return False


    def open(self):
        if not self.open:
            self.gui.open()
            self.open = True


    def close(self):
        """
        Closes all child windows, then itself.
        """
        for window in self.child_windows:
            if window.is_open():
                window.close()

        self.gui.close()
        self.open = False
        close_signal.emit(0)


    def add_child_window(self, child_window: 'Window'):
        self.child_windows.append(child_window)


    def remove_child_window(self, child_window: 'Window'):
        self.child_windows.remove(child_window)
