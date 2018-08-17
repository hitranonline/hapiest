from typing import List

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton, QCompleter

from utils.metadata.molecule import MoleculeMeta
from utils.xsc import CrossSectionMeta, CrossSectionFilter
from worker.hapi_worker import HapiWorker, WorkRequest


class CrossSectionFetchWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.parent = parent

        self.wn_check: QCheckBox = None
        self.wn_min: QDoubleSpinBox = None
        self.wn_max: QDoubleSpinBox = None

        self.pressure_check: QCheckBox = None
        self.pressure_min: QDoubleSpinBox = None
        self.pressure_max: QDoubleSpinBox = None

        self.temp_check: QCheckBox = None
        self.temp_min: QDoubleSpinBox = None
        self.temp_max: QDoubleSpinBox = None

        self.molecule: QComboBox = None
        self.cross_section: QComboBox = None

        self.fetch_button: QPushButton = None
        self.apply_filters: QPushButton = None

        self.cross_section_meta: CrossSectionMeta = None

        self.fetching = False

        uic.loadUi('layouts/cross_section_widget.ui', self)

        self.pressure_check.toggled.connect(self.gen_toggle_function([self.pressure_max, self.pressure_min]))
        self.temp_check.toggled.connect(self.gen_toggle_function([self.temp_max, self.temp_min]))
        self.wn_check.toggled.connect(self.gen_toggle_function([self.wn_max, self.wn_min]))

        self.pressure_check.setChecked(True)
        self.temp_check.setChecked(True)
        self.wn_check.setChecked(True)

        self.temp_check.toggle()
        self.wn_check.toggle()
        self.pressure_check.toggle()

        self.fetch_button.clicked.connect(self.__on_fetch_clicked)
        self.apply_filters.clicked.connect(self.__on_apply_filters_clicked)

        self.molecule.addItems(MoleculeMeta.all_names())
        self.molecule.setEditable(True)
        self.completer: QCompleter = QCompleter(MoleculeMeta.all_names(), self)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitive)
        self.molecule.setCompleter(self.completer)

        self.molecule.currentTextChanged.connect(self.__on_molecule_selection_changed)
        self.__on_molecule_selection_changed(self.molecule.currentText())

    def gen_toggle_function(self, other_widgets: List[QWidget]):
        return lambda checked: list(map(lambda widget: widget.setDisabled(not checked), other_widgets))

    ###
    # Event handlers
    ###

    def __on_apply_filters_clicked(self, _checked: bool):
        if self.pressure_check.isChecked():
            pressure = [self.pressure_min.value(), self.pressure_max.value()]
            pressure.sort()
        else:
            pressure = None

        if self.wn_check.isChecked():
            wn = [self.wn_min.value(), self.pressure_max.value()]
            wn.sort()
        else:
            wn = None

        if self.temp_check.isChecked():
            temp = [self.temp_min.value(), self.temp_max.value()]
            temp.sort()
        else:
            temp = None

        filter = CrossSectionFilter(self.get_selected_molecule_id(), wn, pressure, temp)

        self.cross_section.clear()
        self.cross_section.addItems(filter.get_cross_sections())

    def __on_molecule_selection_changed(self, _current_text: str):
        self.cross_section_meta = CrossSectionMeta(self.get_selected_molecule_id())
        self.cross_section.clear()
        items = self.cross_section_meta.get_all_filenames()
        self.cross_section.addItems(items)

        if self.fetching:
            return

        if len(items) == 0:
            self.fetch_button.setDisabled(True)
        else:
            self.fetch_button.setEnabled(True)

    def __on_fetch_clicked(self, _checked: bool):
        args = HapiWorker.echo(name=self.cross_section.currentText())
        self.fetch_button.setDisabled(True)
        self.worker = HapiWorker(WorkRequest.DOWNLOAD_XSC, args, self.__on_fetch_xsc_done)
        self.worker.start()

    def __on_fetch_xsc_done(self, res):
        _result = res.result
        self.parent.populate_table_lists()
        self.fetching = False
        self.fetch_button.setEnabled(True)

    ###
    # Getters
    ###

    def get_selected_molecule_id(self) -> int:
        selected_molecule_name = self.molecule.currentText()
        mid = MoleculeMeta(selected_molecule_name)
        return mid.id
