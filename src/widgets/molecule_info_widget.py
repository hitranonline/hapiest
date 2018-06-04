from PyQt5.QtCore.Qt import *
from PyQt5.QtWidgets import *
import json
import utils.log

class MoleculeInfoWidget(QScrollArea):

    FIELDS = ['Formula', 'InChi', 'InChiKey', 'HITRANonline_ID', 'Categories', 'Aliases']

    def __init__(self, json_file_name = None, parent = None):
        QScrollArea.__init__(self, parent)
        
        def create_field(text):
            field_name = text.lower()
            label = QLabel('<b>{}:</b>'.format(text))
            value = QLabel()
        
            label.setTextFormat(TextFormat.RichText)
            value.setTextFormat(TextFormat.RichText)
            
            self.__dict__[field_name + "_label"] = label
            self.__dict__[field_name] = value

        self.name = QLabel()
        self.img = QWidget()
        
        map(create_field, MoleculeInfoWidget.FIELDS)

        self.aliases.setWordWrap(True)
        self.categories.setWordWrap(True)

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        
        map(lambda x: self.form_layout.addRow(self.__dict__[x.lower() + '_label'], self.__dict__[x.lower()]), MoleculeInfoWidget.FIELDS)

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.img)
        self.hlayout.addWidget(self.name)

        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.addWidget(self.hlayout)
        self.vlayout.addWidget(self.form_layout)
        self.setWidget(self.vlayout)

        if json_file_name == None:
            pass
        else:
            self.data = None
            try:
                with open('res/molecules/{}.json'.format(json_file_name), 'r') as file:
                    text = file.read()
                    self.data = json.loads(text)
            except Exception as e:
                log('No such molecule \'{}\''.format(json_file_name)) 
            if self.data != None:
                self.restructure_aliases()
                try:
                    self.name.setText(self.data['short_alias'])
                    self.formula.setText(self.data['ordinary_formula_html'])
                    if 'hitranonline_id' in self.data and self.data['hitranonline_id'] != None:
                        self.hitranonline_id.setText(str(self.data['hitranonline_id']))
                    self.inchi.setText(self.data['inchi'])
                    self.inchikey.setText(self.data['aliases']['inchikey'])
                    
                    alias_text = ''
                    for ty, alias in self.data['aliases'].items():
                        alias_text = '{}<br>{}: {}'.format(alias_text, str(ty), str(alias))
                    self.aliases.setText(alias_text)

                    categories_text = ''
                    for categorie in self.data['categories']:
                        categories_text = '{}<br>{}'.format(categories_text, str(categorie))
                    self.categories.setText(categories_text)

                except Exception as e:
                    err_log('Encountered error \'{}\' - likely a malformed molecule json file'.format(str(e)))

    def restructure_aliases(self):
        if 'aliases' in self.data:
            reformatted = {}
            for item in self.data['aliases'].items():
                reformatted[item['type']] = item['alias']
            self.data['aliases'] = reformatted
 
