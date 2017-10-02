class FetchWindow(object):

    def __init__(self):
        self.gui = FetchWindowGui(self)
        self.is_open = True

    def display_graph(self, graph):
        self.child_windows.append(graph)
        # TODO: Implement this

    def close(self):
        self.gui.close()

    def try_fetch(self):
        # TODO: Implement this
