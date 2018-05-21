from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.isotopologue import *
from widgets.main_window_gui import MainWindowGui
from utils.log import *
from utils.fetch_error import FetchErrorKind, FetchError
from worker.work_result import *
from windows.window import Window

class MainWindow(Window):
    def __init__(self):
        Window.__init__(self, MainWindowGui(self), None)


    def fetch_done(self, work_result: WorkResult):
        """
        User feedback for GUI paramter fields of the fetch function in the Main Window.

        @param work_result contains the work result (error or success)
        """
        try:
            self.gui.fetch_handler.worker.safe_exit()
            result = work_result.result
            self.enable_fetch_button()
            if result != None and 'all_tables' in result:
                log("Successfully finished fetch.")
                self.gui.populate_table_lists(result['all_tables'])
                return
            log("Failed to fetch...")
            if isinstance(result, List):
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
        except Exception as e:
            debug(e)

    def disable_fetch_button(self):
        """
        Disable fetch button to disallow user to stack data requests.
        
        """
        self.gui.fetch_button.setDisabled(True)

    def enable_fetch_button(self):
        """
        Re-enables fetch button to allow user to request data.
    
        """
        self.gui.fetch_button.setEnabled(True)

    def open_graph_window(self):
        """
        TODO: Implement this method?
        
        """
        raise Exception("Unsupported: graph operation")

    def close_window(self, to_close):
        """
        Close all occurences of the window to_close in the windows list.
        
        @param to_close Window to be closed
        
        """
        self.child_windows = filter(
            lambda window: window != to_close, self.child_windows)
        to_close.close()

    def close(self):
        """
        Closes window.
    
        """
        for window in self.child_windows:
            if window.is_open:
                window.close()

        self.gui.close()

    def open(self):
        """
        Opens the Main Window GUI.
        
        """
        self.gui.open()


    def text_log(self, text):
        """
        Sets status_bar_label to text mode to display console output when append_text signal received.
        """
        self.gui.status_bar_label.setText(text)


    def html_log(self, html):
        """
        Sets status_bar_label to html mode to display html to console output.
        """
        self.gui.status_bar_label.setText(html)
