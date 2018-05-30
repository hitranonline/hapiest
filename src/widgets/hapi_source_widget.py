from PyQt5 import QtWidgets, QtCore, uic, QtGui
from types import *
from typing import *

class HapiSourceWidget(QtWidgets.QTextEdit):
    def __init__(self, title: str, authors: List[str], year: str, doi: Optional[str]):
        self.title = title
        self.authors = authors
        self.year = year
        if doi == None:
            self.doi = ''
        else:
            self.doi = doi

        QtWidgets.QTextEdit.__init__(self)
        self.setReadOnly(True)
        self.setAcceptRichText(True)
        self.setHtml(self.generate_plain_text())
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)

    def create_plain_doi_str(self):
        if self.doi == '':
            return '';
        else:
            return 'DOI: {}'.format(self.doi)

    def generate_latex(self) -> str:
        pass

    def generate_html(self) -> str:
        pass
    
    def generate_plain_text(self) -> str:
        authors_str = ''
        for author in self.authors:
            authors_str = '{}{}, '.format(authors_str, author)
        return '{}{} ({}){}'.format(authors_str, self.title, self.year, self.create_plain_doi_str()).strip()
