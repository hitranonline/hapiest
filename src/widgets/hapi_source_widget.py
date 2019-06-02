from typing import *

from PyQt5 import QtWidgets


class HapiSourceWidget(QtWidgets.QTextEdit):

    def __init__(self, title: str, authors: List[str], year: str, doi: Optional[str],
                 journal: Optional[str] = None, volume: Optional[str] = None,
                 page_start: Optional[int] = None, page_end: Optional[int] = None, **_kwargs):
        self.title = title
        self.authors = authors
        self.year = year
        self.journal = journal
        self.volume = volume
        self.page_start = page_start
        self.page_end = page_end

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
            return f'DOI: {self.doi}'

    def generate_latex(self) -> str:
        pass

    def generate_html(self) -> str:
        pass

    def generate_plain_text(self) -> str:
        authors_str = ''
        l = len(self.authors) - 1
        for i in range(0, l):  # author in self.authors:
            authors_str = '{}{}, '.format(authors_str, self.authors[i])
        authors_str = '{}{}.'.format(authors_str, self.authors[l])

        journal_str = ''
        if self.journal != None:
            journal_str += self.journal
            if self.volume != None:
                journal_str += ' {},'.format(self.volume)
            if self.page_start != None:
                if self.page_end == None:
                    journal_str += ' {}'.format(self.page_start)
                else:
                    journal_str += ' {}-{}'.format(self.page_start, self.page_end)

        return '{} {}. {} ({}). {}'.format(authors_str, self.title, journal_str, self.year,
                                           self.create_plain_doi_str()).strip()
