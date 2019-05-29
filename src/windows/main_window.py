from widgets.main_window_gui import MainWindowGui
from windows.window import Window


class MainWindow(Window):
    def __init__(self):
        Window.__init__(self, MainWindowGui(self), None)

    def open(self):
        """
        Opens the Main Window GUI.
        
        """
        self.gui.open()

    def text_log(self, text):
        """
        Sets status_bar_label to text mode to display console output when append_text signal
        received.
        """
        self.gui.status_bar_label.setText(text)

    def html_log(self, html):
        """
        Sets status_bar_label to html mode to display html to console output.
        """
        self.gui.status_bar_label.setText(html)
