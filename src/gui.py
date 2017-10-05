class Gui(object):
    def __init__(self):
        self.gui = QtGui.QWidget()

    # Set the size to the specified dimensions
    def set_size(self, height, width):
        self.window.setGeometry(0, 0, width, height)
        # In order to see the new size, updateGeometry must be called
        self.window.updateGeometry()

    # Changes the title of the window
    def set_title(self, title):
        self.window.setWindowTitle(title)

    def open(self):
        raise NotImplementedError("Should have implemented this")
