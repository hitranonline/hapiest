from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from metadata.molecule_meta import MoleculeMeta
from utils.hapiest_util import program_icon
from utils.log import *


class MoleculeInfoWidget(QWidget):
    FIELDS = ['Formula', 'InChi', 'InChiKey', 'HITRANonline_ID', 'Aliases']

    def __init__(self, molecule_name, parent=None):
        QWidget.__init__(self, parent)

        self.setWindowIcon(program_icon())

        def create_field(text):
            field_name = text.lower()
            label = QLabel('<b>{}:</b>'.format(text))
            value = QLabel()
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setTextFormat(Qt.RichText)
            value.setTextFormat(Qt.RichText)

            self.__dict__[field_name + "_label"] = label
            self.__dict__[field_name] = value

        self.setObjectName('MoleculeInfoWidget')

        self.name = QLabel()
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
        self.vlayout.addLayout(self.form_layout)
        # self.vlayout.addItem(QSpacerItem(1, 1, QSizePolicy.Preferred, QSizePolicy.Expanding))
        self.hlayout.addLayout(self.vlayout)
        self.hlayout.addItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Preferred))

        self.container_layout = QVBoxLayout()
        self.container_layout.addLayout(self.hlayout)
        spacer = QSpacerItem(1, 1, QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.container_layout.addItem(spacer)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.vlayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.hlayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.form_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.setLayout(self.container_layout)

        self.molecule = MoleculeMeta(molecule_name)
        formula = self.molecule.formula
        if self.molecule.is_populated():
            self.img.setAttribute(Qt.WA_StyledBackground)
            self.img.setStyleSheet(
                f'border-image: url("res/img/molecules/{formula}.gif") 0 0 0 0 stretch stretch;')
            self.img.show()

            self.restructure_aliases()
            try:
                self.name.setText('<span style="font-size: 16pt"><i><b>{}</b></i></span>'.format(
                    self.molecule.formula))
                self.formula.setText(self.molecule.html)
                self.hitranonline_id.setText(str(self.molecule.id))
                self.inchi.setText(self.molecule.inchi)
                self.inchikey.setText(self.molecule.inchikey)

                alias_text = ''
                for _, alias in self.molecule.aliases.items():
                    alias_text = '{}<br><i>{}</i>'.format(alias_text, str(alias))
                self.aliases.setText(alias_text)

            except Exception as e:
                err_log('Encountered error \'{}\' - likely a malformed molecule json file'.format(
                    str(e)))

            self.adjustSize()

    def restructure_aliases(self):
        reformatted = {}
        for item in self.molecule.aliases:
            reformatted[item['type']] = item['alias']
        self.molecule.aliases = reformatted
