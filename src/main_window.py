from option import *

class MainWindow(object):
    def __init__(self):
        # Initially an empty list, until other windows are created
        self.child_windows = []

        # Create a data handle that points to nothing
        self.selected_data = DataHandle(None())

        # Create a new instance of the GUI container class
        self.gui = MainWindowGui(self)

        self.is_open = True

    def fetch(self):
        # Open a fetch window
        self.child_windows.append(FetchWindow(self))

    def close_window(self, to_close):
        # Close all occurences of the window to_close in the windows list.
        # There should only be one but you never know...
        self.child_windows =
            filter(lambda window: window != to_close, self.child_windows)
        to_close.close()

    def close(self):
        for window in self.child_windows: if window.is_open: window.close()
        self.gui.close()
