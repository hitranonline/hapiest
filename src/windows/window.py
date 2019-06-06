from typing import Set

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget


class Window(QtCore.QObject):

    def __init__(self, gui: QWidget, parent: 'Window'):
        super(Window, self).__init__()

        self.parent: Window = parent
        self.gui: QWidget = gui
        self.child_windows: Set[Window] = set()

        self.open = False

    # def event(self, e):
    #    if e.type() == QtCore.QEvent.User:
    #        self.widget.show()
    #        return True
    #    return False

    def open(self):
        if not self.open and self.parent:
            self.gui.show()
            self.open = True

    def close(self):
        """
        Closes all child windows, then itself.
        """
        for child in self.child_windows:
            child.close()

        self.gui.close()
        self.open = False

    def add_child_window(self, child: 'Window'):
        self.child_windows.add(child)
