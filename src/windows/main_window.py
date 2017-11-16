from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.hapiest_util import *
from utils.isotopologue import *
from widgets.main_window_gui import MainWindowGui
from utils.log import *
from utils.fetch_handler import *


class MainWindow:
    def __init__(self):
        # Initially an empty list, until other windows are created
        self.child_windows = []

        # Create a new instance of the GUI container class
        self.gui: 'MainWindowGui' = MainWindowGui(self)

        self.is_open: bool = True

    def fetch_done(self, result: Union[bool, List['FetchError'], 'FetchError']):
        self.gui.fetch_handler.worker.exit()
        self.enable_fetch_button()
        if result == True:
            log("Successfully finished fetch.")
            return
        log("Failed to fetch...")
        if isinstance(result, list):
            errs = result
        else:
            errs = [result]
        for err in errs:
            # This means the wavenumber range was too small (probably), so
            # we'll tell the user it is too small
            if err.error == FetchErrorKind.FailedToRetreiveData:
                self.gui.err_small_range.show()
                err_log('The entered wavenumber range is too small, try increasing it')
            # Not much to do in regards to user feedback in this case....
            elif err.error == FetchErrorKind.FailedToOpenThread:
                err_log('Failed to open thread to make query HITRAN')
            elif err.error == FetchErrorKind.BadConnection:
                self.gui.err_bad_connection.show()
                err_log(
                    'Error: Failed to connect to HITRAN. Check your internet connection and try again.')
            elif err.error == FetchErrorKind.BadIsoList:
                self.gui.err_bad_iso_list.show()
                err_log(' Error: You must select at least one isotopologue.')
            elif err.error == FetchErrorKind.EmptyName:
                self.gui.err_empty_name.show()

    def disable_fetch_button(self):
        self.gui.fetch_button.setDisabled(True)

    def enable_fetch_button(self):
        self.gui.fetch_button.setEnabled(True)

    def open_graph_window(self):
        # Open a fetch window
        # self.child_windows.append(GraphWindow())
        raise Exception("Unsupported: graph operation")

    def close_window(self, to_close):
        # Close all occurences of the window to_close in the windows list.
        # There should only be one but you never know...
        self.child_windows = filter(
            lambda window: window != to_close, self.child_windows)
        to_close.close()

    def close(self):
        for window in self.child_windows:
            if window.is_open:
                window.close()

        self.gui.close()

    def open(self):
        self.gui.open()

    # Method that get called when the append_text signal is received by the window
    # This is to allow console output
    def text_log(self, text):
        self.gui.status_bar_label.setText("l")
        self.gui.status_bar_label.setText(text)

    # Method gets called when html formatted text is to be printed to console.
    def html_log(self, html):
        self.gui.status_bar_label.setText(html)
