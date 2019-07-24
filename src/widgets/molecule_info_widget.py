from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from metadata.molecule_meta import MoleculeMeta
from metadata.xsc_meta import CrossSectionMeta
from utils.hapiest_util import program_icon, Config
from utils.log import *
from widgets.fetch_widget import FetchWidget
from widgets.cross_section_fetch_widget import CrossSectionFetchWidget


class MoleculeInfoWidget(QWidget):
    FIELDS = ['Formula', 'InChI', 'InChIKey', 'HITRANonline_ID', 'Aliases']

    def __init__(self, molecule_name, parent):
        QWidget.__init__(self, parent)
        self.setStyleSheet("background-color: white;")

        self.molecule = MoleculeMeta(molecule_name)

        if not self.molecule.is_populated():
            raise Exception("Don't make a molecule info widget with an invalid molecule")

        self.fetch_widget: FetchWidget = FetchWidget.FETCH_WIDGET_INSTANCE
        self.xsc_widget: CrossSectionFetchWidget = \
            CrossSectionFetchWidget.CROSS_SECTION_FETCH_WIDGET_INSTANCE
        self.main_gui = parent

        self.parent = parent
        self.setWindowIcon(program_icon())

        def create_field(text):
            field_name = text.lower()
            label = QLabel(f'<b>{text}:</b>')
            value = QLabel()
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setTextFormat(Qt.RichText)
            value.setWordWrap(True)
            value.setTextFormat(Qt.RichText)

            self.__dict__[field_name + "_label"] = label
            self.__dict__[field_name] = value

        self.setObjectName('MoleculeInfoWidget')

        self.name = \
            QLabel(f"<span style='font-size: 16pt'><i><b>{self.molecule.name}</b></i></span>")

        self.button_style = "padding: .1em .2em .1em .2em;"
        self.get_xsc_button = QPushButton("Get cross-sections")
        self.get_xsc_button.pressed.connect(self.__open_cross_sections)
        self.get_xsc_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.get_xsc_button.setStyleSheet(self.button_style)

        self.get_lbl_button = QPushButton("Get line-by-line data")
        self.get_lbl_button.pressed.connect(self.__open_line_by_line)
        self.get_lbl_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.get_lbl_button.setStyleSheet(self.button_style)

        self.img = QWidget()
        self.img.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        if Config.high_dpi:
            self.img.setFixedWidth(300)
            self.img.setFixedHeight(300)
        else:
            self.img.setFixedWidth(400)
            self.img.setFixedHeight(400)

        # Have to call list because map is lazy
        list(map(create_field, MoleculeInfoWidget.FIELDS))

        self.aliases.setWordWrap(True)

        self.form_layout = QFormLayout()

        list(map(lambda x: self.form_layout.addRow(self.__dict__[x.lower() + '_label'],
                                                   self.__dict__[x.lower()]),
                 MoleculeInfoWidget.FIELDS))

        self.button_container = QHBoxLayout()

        if self.molecule.has_lbl_data:
            self.button_container.addWidget(self.get_lbl_button)
        if len(CrossSectionMeta(self.molecule.id).metas) > 0:
            self.button_container.addWidget(self.get_xsc_button)

        self.button_spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.button_container.addSpacerItem(self.button_spacer)

        self.img_layout = QVBoxLayout()
        self.img_layout.addWidget(self.img)
        self.img_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Fixed, QSizePolicy.Expanding))

        self.info_layout = QVBoxLayout()
        self.info_layout.addWidget(self.name)
        self.info_layout.addLayout(self.button_container)
        self.info_layout.addLayout(self.form_layout)
        self.info_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Fixed, QSizePolicy.Expanding))

        self.central_layout = QHBoxLayout()
        self.central_layout.addLayout(self.img_layout)
        self.central_layout.addSpacerItem(QSpacerItem(50, 1, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.central_layout.addLayout(self.info_layout)
        self.central_layout.addSpacerItem(
                QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(self.central_layout)

        formula = self.molecule.formula
        if self.molecule.is_populated():
            self.img.setAttribute(Qt.WA_StyledBackground)
            self.img.setStyleSheet(
                f'border-image: url("res/img/molecules/{formula}.gif") 0 0 0 0 stretch stretch;')
            self.img.show()

            try:
                self.formula.setText(self.molecule.html)
                self.hitranonline_id.setText(str(self.molecule.id))
                self.inchi.setText(self.molecule.inchi)
                self.inchikey.setText(self.molecule.inchikey)

                alias_text = ''
                for alias in self.molecule.aliases:
                    alias_text = f'{alias_text}<i>{alias.alias}</i><hr>'
                self.aliases.setText(alias_text)

            except Exception as e:
                err_log(f'Encountered error \'{str(e)}\' - likely a malformed molecule json file')

            self.adjustSize()

    def __open_cross_sections(self, *_args):
        self.xsc_widget.molecule.setCurrentText(self.molecule.name)
        self.main_gui.tab_widget.setCurrentWidget(self.main_gui.cross_section_tab)

    def __open_line_by_line(self, *_args):
        self.fetch_widget.set_molecule_id(self.molecule.name)
        self.main_gui.tab_widget.setCurrentWidget(self.main_gui.fetch_tab)
