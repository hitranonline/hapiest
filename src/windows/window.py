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
        
        self.close_signal.connect(self.__close_signal_handler)
        self.gui.set_on_close(lambda: self.close_signal.emit(self))
        self.is_open = False
    
    #def event(self, e):
    #    if e.type() == QtCore.QEvent.User:
    #        self.widget.show()
    #        return True
    #    return False

    def __close_signal_handler(self, to_remove):
        if self.parent != None:
            self.parent.remove_child_window(to_remove)

    def open(self):
        if not self.is_open:
            self.gui.show()
            self.is_open = True


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
        print("removing from" + str(self))
        try:
            self.child_windows.remove(child_window)
        except Exception as e:
            print(str(e))
