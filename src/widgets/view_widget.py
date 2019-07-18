from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *

from utils.hapiest_util import program_icon
from widgets.hapi_table_view import HapiTableView


class ViewWidget(QWidget):
    instances = []

    @staticmethod
    def set_table_names(table_names):
        for widget in ViewWidget.instances:
            widget.table_name.clear()
            widget.table_name.addItems(list(table_names))

    def __init__(self, parent=None):
        QWidget.__init__(self)

        ViewWidget.instances.append(self)

        self.parent = parent

        self.table: HapiTableView = None
        self.back_button: QToolButton = None
        self.next_button: QToolButton = None
        self.view_button: QPushButton = None
        self.table_container: QWidget = None
        self.save_button: QPushButton = None
        self.output_name: QLineEdit = None
        self.table_name: QComboBox = None
        self.editing_enabled: QCheckBox = None

        uic.loadUi('layouts/view_widget.ui', self)

        self.setWindowIcon(program_icon())
        self.setWindowTitle("View")

        self.view_button.clicked.connect(self.__on_view_button_click)
        self.editing_enabled.toggled.connect(self.__on_editing_enabled_checked)

        # Uncomment the following two lines to enable auto-loading of the first detected table.
        # if 0 != self.table_name.count():
        #    self.__on_view_button_click()

        self.back_button.setToolTip("(Edit) Previous page.")
        self.next_button.setToolTip("(Edit) Next page.")
        self.view_button.setToolTip("Opens interactable data table.")

    def closeEvent(self, a0: QtGui.QCloseEvent):
        ViewWidget.instances.remove(self)
        QWidget.closeEvent(self, a0)

    ###
    # Event Handlers
    ###

    def __on_editing_enabled_checked(self, checked):
        if self.table:
            self.table.set_read_only(not checked)
            self.table.update_dirty_cells()

    def __on_view_button_click(self):
        """
        *Disables view button, displays table.*
        """
        table_name = self.get_table_name()
        if not table_name:
            return
        self.view_button.setDisabled(True)
        if self.table:
            self.table.close_table()
            self.table.close()
            QWidget().setLayout(self.table_container.layout())
        else:
            self.editing_enabled.setEnabled(True)

        self.table = HapiTableView(self, table_name)
        self.table.set_read_only(True)
        self.editing_enabled.setChecked(False)

        layout = QtWidgets.QGridLayout(self.table_container)
        layout.addWidget(self.table)
        self.table_container.setLayout(layout)

    ###
    # Getters
    ###

    def get_table_name(self):
        """
        *Returns the name of the table entered by user for edit tab.*
        """
        return self.table_name.currentText()

    def get_output_name(self):
        """
        *Returns name of destination table name entered in by user.*
        """
        return self.output_name.text()
