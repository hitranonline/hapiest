from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json
from widgets.gui import GUI
from utils.log import *
from utils.isotopologue import Isotopologue

class MoleculeInfoWidget(QScrollArea, GUI):

    FIELDS = ['Formula', 'InChi', 'InChiKey', 'HITRANonline_ID', 'Categories', 'Aliases']

    def __init__(self, json_file_name = None, parent = None):
        QScrollArea.__init__(self, parent)
        GUI.__init__(self)
        
        def create_field(text):
            field_name = text.lower()
            label = QLabel('<b>{}:</b>'.format(text))
            value = QLabel()
            value.setTextInteractionFlags(Qt.TextSelectableByMouse); 
            label.setTextFormat(Qt.RichText)
            value.setTextFormat(Qt.RichText)
            
            self.__dict__[field_name + "_label"] = label
            self.__dict__[field_name] = value

        self.setObjectName('MoleculeInfoWidget')
        
        self.name = QLabel()
        self.img = QWidget()
        self.img.setMinimumWidth(256)
        self.img.setMaximumWidth(256)
        self.img.setMinimumHeight(256)
        self.img.setMaximumHeight(256)

        # Have to call list because map is lazy
        list(map(create_field, MoleculeInfoWidget.FIELDS))

        self.aliases.setWordWrap(True)
        self.categories.setWordWrap(True)

        self.form_layout = QFormLayout()
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        
        list(map(lambda x: self.form_layout.addRow(self.__dict__[x.lower() + '_label'], self.__dict__[x.lower()]), MoleculeInfoWidget.FIELDS))

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.img)
        
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.name)
        self.vlayout.addLayout(self.form_layout)
        self.hlayout.addLayout(self.vlayout)
        
        self.container = QWidget()
        self.container.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.vlayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.hlayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.form_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.container.setLayout(self.hlayout)
        self.setWidget(self.container)
        
        if json_file_name != None:
            self.img.setAttribute(Qt.WA_StyledBackground)
            self.img.setStyleSheet('border-image: url("res/img/molecules/{}.png") 0 0 0 0 stretch stretch;'.format(json_file_name))
            self.img.show()
            self.data = None
            try:
                with open('res/molecules/{}.json'.format(json_file_name), 'r') as file:
                    text = file.read()
                    self.data = json.loads(text)
            except Exception as e:
                log('No such molecule \'{}\' with error {}'.format(json_file_name, str(e))) 
            if self.data != None:
                self.restructure_aliases()
                try:
                    self.name.setText('<span style="font-size: 16pt"><i><b>{}</b></i></span>'.format(self.data['short_alias']))
                    self.formula.setText(self.data['ordinary_formula_html'])
                    if 'hitranonline_id' in self.data and self.data['hitranonline_id'] != None:
                        self.hitranonline_id.setText(str(self.data['hitranonline_id']))
                    else:
                        self.hitranonline_id.setText(str(Isotopologue.from_molecule_name(self.data['ordinary_formula']).id))
                    self.inchi.setText(self.data['inchi'])
                    self.inchikey.setText(self.data['aliases']['inchikey'])
                    
                    alias_text = ''
                    for ty, alias in self.data['aliases'].items():
                        alias_text = '{}<br><b>{}</b>: <i>{}</i>'.format(alias_text, str(ty), str(alias))
                    self.aliases.setText(alias_text)

                    categories_text = ''
                    for categorie in self.data['categories']:
                        categories_text = '{}<br>{}'.format(categories_text, str(categorie))
                    self.categories.setText(categories_text)
                    
                except Exception as e:
                    err_log('Encountered error \'{}\' - likely a malformed molecule json file'.format(str(e)))
                
                self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.setMinimumWidth(self.container.geometry().width())
                self.setWidgetResizable(True)
                self.widget().adjustSize()
                self.adjustSize()
         
    def restructure_aliases(self):
        if 'aliases' in self.data:
            reformatted = {}
            for item in self.data['aliases']:
                reformatted[item['type']] = item['alias']
            self.data['aliases'] = reformatted
 
