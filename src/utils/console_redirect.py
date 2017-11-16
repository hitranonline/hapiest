from multiprocessing import Queue
from PyQt5 import QtCore


# A class that can be used to redirect output from stdout and stderr to a
# QTextEdit
class TextEditStream():
    def __init__(self, window):
        self.queue = Queue()
        self.window = window

    def write(self, text):
        self.queue.put((0, str(text)))

    def write_html(self, html):
        self.queue.put((1, html))

    def flush(self):
        pass


# An object that will hang out in the background and receive all outputs
class TextReceiver(QtCore.QObject):
    write_text_signal = QtCore.pyqtSignal(str)
    write_html_signal = QtCore.pyqtSignal(str)

    TEXT_EDIT_STREAM = None
    TEXT_RECEIVER = None
    TEXT_THREAD = None
    WINDOW = None

    @staticmethod
    def redirect_close():
        TextReceiver.TEXT_RECEIVER.running = False
        TextReceiver.TEXT_THREAD.terminate()

    @staticmethod
    def init_console_redirect(main_window, *args, **kwargs):
        TextReceiver.TEXT_EDIT_STREAM = TextEditStream(main_window)

        TextReceiver.WINDOW = main_window
        # Create a receiver
        TextReceiver.TEXT_RECEIVER = TextReceiver(TextReceiver.TEXT_EDIT_STREAM.queue, *args, **kwargs)
        # Create a thread for the receiver to run in
        TextReceiver.TEXT_THREAD = QtCore.QThread()
        # Connect the signal to the console output handler in the main window
        # Connect the console output signals
        TextReceiver.TEXT_RECEIVER.write_text_signal.connect(lambda str: main_window.text_log(str))
        TextReceiver.TEXT_RECEIVER.write_html_signal.connect(lambda html: main_window.html_log(html))
        # Move the receiver to the background thread
        TextReceiver.TEXT_RECEIVER.moveToThread(TextReceiver.TEXT_THREAD)
        # When the thread starts, start the text receiver
        TextReceiver.TEXT_THREAD.started.connect(TextReceiver.TEXT_RECEIVER.run)
        # Start thread
        TextReceiver.TEXT_THREAD.start()

    def __init__(self, queue, *args, **kwargs):
        QtCore.QObject.__init__(self)
        self.queue = queue
        self.running = True

    def run(self):
        while self.running:
            (ty, text) = self.queue.get()
            if ty == 0:
                self.write_text_signal.emit(text)
            else:
                self.write_html_signal.emit(text)
