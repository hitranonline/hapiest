
class GUI:
    """
    A GUI class is an entire window; not just a single component or widget in a gui.
    """

    def __init__(self):
        # super(GUI, self).__init__()
        self.on_close_fn = lambda: ()

    def set_on_close(self, on_close_fn):
        self.on_close_fn = on_close_fn

    def closeEvent(self, event):
        self.on_close_fn()
        event.accept()

    def reject(self):
        self.on_close_fn()
