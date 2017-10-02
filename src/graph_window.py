class GraphWindow(object):

    # Data should never be None / null, since if there is no data selected a new
    # graphing window shouldn't even be opened.
    def __init__(self, data, graph_type):
        # Child windows of the graph window will be all the windows with graphs
        # it opens
        self.child_windows = []

        self.gui = GraphWindowGui(self, graph_type)
        self.graph_type = graph_type
        self.data = data
        self.is_open = True

    def try_render_graph(self):
        # TODO: Implement this

    def display_graph(self, graph):
        self.child_windows.append(graph)
        # TODO: Implement this

    def close(self):
        for window in child_windows: if window.is_open: window.close()
        self.gui.close()
