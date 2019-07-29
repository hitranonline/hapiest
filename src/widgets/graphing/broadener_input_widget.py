from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox, QSpacerItem, QSizePolicy, \
    QDoubleSpinBox, QComboBox, QPushButton, QVBoxLayout, QScrollArea

from metadata.parameter_availability import ParameterAvailability
from metadata.hapi_metadata import HapiMetaData
from metadata.table_header import TableHeader


class BroadenerItemWidget(QWidget):

    def __init__(self, parent, broadener: str):
        QWidget.__init__(self, parent)
        
        self._parent = parent

        self.broadener = broadener

        self.enabled = QCheckBox()
        self.enabled.clicked.connect(self.__on_enabled_toggled)

        self.name = QLabel(broadener)
        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding)

        # Spin box with two decimal places, constant size, range from 0 to 1
        self.proportion = QDoubleSpinBox()
        self.proportion.valueChanged.connect(self.__on_value_changed)
        self.proportion.setDecimals(2)
        self.proportion.setRange(0.0, 1.0)
        self.proportion.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.proportion.setDisabled(True)

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.enabled)
        self.hlayout.addWidget(self.name)
        self.hlayout.addSpacerItem(self.hspacer)
        self.hlayout.addWidget(self.proportion)

        self.hlayout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

        self.setLayout(self.hlayout)

    def __on_value_changed(self, checked):
        self._parent.on_value_updated()

    def __on_enabled_toggled(self, checked):
        self.proportion.setEnabled(checked)

    def is_enabled(self):
        return self.enabled.isChecked()

    def get_value(self):
        return self.proportion.value()


class BroadenerInputWidget(QWidget):

    BROADENERS = {"gamma_co2", "gamma_h2", "gamma_he", "gamma_h2o"}

    BROADENER_NAME_MAP = {
        "gamma_co2": "CO2",
        "gamma_h2": "H2",
        "gamma_he": "He",
        "gamma_h2o": "H2O"
        }

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.parent = parent

        self.table: TableHeader = None

        self.broadeners = set()
        self.broadener_items = {}

        self.broadener_item_layout = QVBoxLayout()
        self.broadener_items_container = QWidget()
        self.broadener_items_container.setLayout(self.broadener_item_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.broadener_items_container)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

        self.update_widgets()

    def set_table(self, table_name):
        table = TableHeader(table_name)
        self.table = table
        if table_name.endswith(".xsc"):
            hmd = None
            self.broadeners = set()
            return
        hmd = HapiMetaData(table_name)

        parameter_availability = ParameterAvailability(hmd.molecule_id())

        # This table is either not a table, or missing a header. In either case, it cant be used
        if not table.populated:
            self.setDisabled(True)
            return

        self.setEnabled(True)

        extras = set(table.extra)
        broadeners = BroadenerInputWidget.BROADENERS.intersection(extras)

        # Go from 'gamma_CO2' to 'CO2'
        self.broadeners = {BroadenerInputWidget.BROADENER_NAME_MAP[b] for b in broadeners}
        self.broadeners.add("self")
        self.broadeners.add("air")
        self.update_widgets()

    def get_diluent(self):
        diluent = {}

        for name in self.broadeners:
            if self.broadener_items[name].is_enabled():
                diluent[name] = self.broadener_items[name].get_value()

        return diluent

    def update_widgets(self):
        # Removes all items from broadener_item_layout, and adds the ones that are in
        # added_broadener_names. Then updates selected_broadener to only contain the names
        # of broadeners that have not yet been added

        while True:
            a = self.broadener_item_layout.takeAt(0)
            if a is None:
                break
            a.widget().hide()

        broadeners = list(self.broadeners)  # Clone the list so we dont modify it

        # If you call remove on a set and the element is not in there it will throw an exception
        if "self" in broadeners:
            broadeners.remove("self")
        if "air" in broadeners:
            broadeners.remove("air")

        def show(name):
            if name not in self.broadener_items:
                self.broadener_items[name] = BroadenerItemWidget(self, name)

            self.broadener_items[name].show()
            self.broadener_item_layout.addWidget(self.broadener_items[name])

        show("self")
        show("air")

        for name in broadeners:
            show(name)

    def on_value_updated(self):
        pass # self.parent.on_value_updated()
