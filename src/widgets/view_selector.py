from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ViewSelector(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self)
        self.parent = parent
        uic.loadUi('layouts/view_selector.ui', self)
        self.buttons.accepted.connect(self.__on_accepted)
        self.show()
        self.buttons.rejected.connect(self.hide)

    def __on_accepted(self):
        xmin, xmax = (self.xmin.value(), self.xmax.value())
        ymin, ymax = (self.ymin.value(), self.ymax.value())
        self.parent.set_viewport(xmin, xmax, ymin, ymax)
        self.hide()
