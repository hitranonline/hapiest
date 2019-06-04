from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from metadata.molecule_meta import MoleculeMeta
from utils.hapiest_util import program_icon
from utils.log import *
from widgets.fetch_widget import FetchWidget
from widgets.cross_section_fetch_widget import CrossSectionFetchWidget

class MoleculeInfoWidget(QWidget):
    FIELDS = ['Formula', 'InChI', 'InChIKey', 'HITRANonline_ID', 'Aliases']

    def __init__(self, molecule_name, parent):
        QWidget.__init__(self, parent)

        self.fetch_widget: FetchWidget = FetchWidget.FETCH_WIDGET_INSTANCE
        self.xsc_widget: CrossSectionFetchWidget = CrossSectionFetchWidget.CROSS_SECTION_FETCH_WIDGET_INSTANCE
        self.main_gui = parent

        self.parent = parent
        self.setWindowIcon(program_icon())

        def create_field(text):
            field_name = text.lower()
            label = QLabel('<b>{}:</b>'.format(text))
            value = QLabel()
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setTextFormat(Qt.RichText)
            value.setWordWrap(True)
            value.setTextFormat(Qt.RichText)

            self.__dict__[field_name + "_label"] = label
            self.__dict__[field_name] = value

        self.setObjectName('MoleculeInfoWidget')

        self.name = QLabel()
        self.get_data_button = QPushButton()
        self.img = QWidget()
        self.img.setMinimumWidth(400)
        self.img.setMaximumWidth(400)
        self.img.setMinimumHeight(400)
        self.img.setMaximumHeight(400)

        # Have to call list because map is lazy
        list(map(create_field, MoleculeInfoWidget.FIELDS))

        self.aliases.setWordWrap(True)

        self.form_layout = QFormLayout()
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        list(map(lambda x: self.form_layout.addRow(self.__dict__[x.lower() + '_label'],
                                                   self.__dict__[x.lower()]),
                 MoleculeInfoWidget.FIELDS))

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.img)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.name)
        self.vlayout.addWidget(self.get_data_button)
        self.vlayout.addLayout(self.form_layout)
        self.vlayout.addItem(QSpacerItem(1, 1, QSizePolicy.Preferred, QSizePolicy.Expanding))
        self.hlayout.addLayout(self.vlayout)
        self.hlayout.addItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Preferred))

        self.container_layout = QVBoxLayout()
        self.container_layout.addLayout(self.hlayout)
        spacer = QSpacerItem(1, 1, QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.container_layout.addItem(spacer)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.vlayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.hlayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.form_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.setLayout(self.container_layout)

        self.molecule = MoleculeMeta(molecule_name)

        if not self.molecule.is_populated():
            raise Exception("Don't make a molecule info widget with an invalid molecule")

        if self.molecule.id < 100:
            text = "Get line-by-line data."
            on_press = self.__open_line_by_line
        else:
            text = "Get cross-sections."
            on_press = self.__open_cross_sections

        self.get_data_button.setText(text)
        self.get_data_button.pressed.connect(on_press)

        formula = self.molecule.formula
        if self.molecule.is_populated():
            self.img.setAttribute(Qt.WA_StyledBackground)
            self.img.setStyleSheet(
                f'border-image: url("res/img/molecules/{formula}.gif") 0 0 0 0 stretch stretch;')
            self.img.show()

            try:
                self.name.setText('<span style="font-size: 16pt"><i><b>{}</b></i></span>'.format(
                    self.molecule.name))
                self.formula.setText(self.molecule.html)
                self.hitranonline_id.setText(str(self.molecule.id))
                self.inchi.setText(self.molecule.inchi)
                self.inchikey.setText(self.molecule.inchikey)

                alias_text = ''
                for alias in self.molecule.aliases:
                    alias_text = '{}<i>{}</i><hr>'.format(alias_text, alias.alias)
                self.aliases.setText(alias_text)

            except Exception as e:
                err_log('Encountered error \'{}\' - likely a malformed molecule json file'.format(
                    str(e)))

            self.adjustSize()

    def __open_cross_sections(self, *_args):
        self.xsc_widget.molecule.setCurrentText(self.molecule.name)
        self.main_gui.tab_widget.setCurrentWidget(self.main_gui.cross_section_tab)

    def __open_line_by_line(self, *_args):
        self.fetch_widget.molecule_id.setCurrentText(self.molecule.name)
        self.main_gui.tab_widget.setCurrentWidget(self.main_gui.fetch_tab)
