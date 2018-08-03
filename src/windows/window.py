from PyQt5 import QtGui, QtWidgets, uic, QtCore
from typing import List
from widgets.gui import GUI

class Window(QtCore.QObject):

    def __init__(self, gui: GUI, parent: 'Window'):
        super(Window, self).__init__()

        self.parent: Window = parent
        self.gui: GUI = gui
        self.child_windows: List[Window] = []
        
        self.is_open = False
    
    #def event(self, e):
    #    if e.type() == QtCore.QEvent.User:
    #        self.widget.show()
    #        return True
    #    return False

    def open(self):
        if not self.is_open and self.parent:
            self.gui.show()
            self.is_open = True


    def close(self):
        """
        Closes all child windows, then itself.
        """
        for i in range(0, len(self.child_windows)):
            self.child_windows[0].close()
            self.child_windows.pop(0)           

        self.gui.close()
        self.open = False



    def add_child_window(self, child_window: 'Window'):
        self.child_windows.append(child_window)
