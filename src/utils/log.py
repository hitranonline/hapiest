import sys
from multiprocessing import Queue

from PyQt5 import QtCore


class TextStream():
    """
    Writes to the appropriate queues.

    """

    def __init__(self, window):
        self.queue = Queue()
        self.window = window

    def write(self, text):
        self.queue.put((0, str(text)))

    def write_html(self, html):
        self.queue.put((1, html))

    def flush(self):
        pass


class TextReceiver(QtCore.QObject):
    """
    Hangs out a background thread and displays messages in the GUI.

    """
    
    write_text_signal = QtCore.pyqtSignal(str)
    write_html_signal = QtCore.pyqtSignal(str)
    
    ## An instance of a TextStream that has the queue that the worker thread reads from
    TEXT_STREAM = None

    ## Receives text and writes it to the status bar
    TEXT_RECEIVER = None

    ## The worker thread
    TEXT_THREAD = None

    ## A reference to the main window
    WINDOW = None


    @staticmethod
    def redirect_close():
        """
        Closes the worker thread

        """
        TextReceiver.TEXT_RECEIVER.running = False
        TextReceiver.TEXT_THREAD.quit()


    @staticmethod
    def init(main_window, *args, **kwargs):
        """
        Initializes the static members of the class and starts the background thread.

        """
        TextReceiver.TEXT_STREAM = TextStream(main_window)

        TextReceiver.WINDOW = main_window
        # Create a receiver
        TextReceiver.TEXT_RECEIVER = TextReceiver(TextReceiver.TEXT_STREAM.queue, *args, **kwargs)
        # Create a thread for the receiver to install.py in
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
        """
    Until the thread should close, read things from the queue and emit the appropriate signal to display them in
    the GUI.

    """
        while self.running:
            (ty, text) = self.queue.get()
            if ty == 0:
                self.write_text_signal.emit(text)
            else:
                self.write_html_signal.emit(text)

def print_html_to_status_bar(arg):
    TextReceiver.TEXT_STREAM.write_html(arg)

def debug(*args, **kwargs):
    """
    Prints directly to stderr.     
    
    """

    print(*args, file=sys.stderr, **kwargs)



def log(arg):
    """
    Prints to the console_output with a fancy lookin log label.

    """
    s = str(arg)
    if TextReceiver.TEXT_STREAM != None:
        if len(s) > 128:
            s = s[0:128]
            print_html_to_status_bar(f'<div style="color: #7878e2">[Log]</div>&nbsp;{s}...')
        else:
            print_html_to_status_bar(f'<div style="color: #7878e2">[Log]</div>&nbsp;{s}')
    print("[Log] ", s, file=sys.__stdout__)


def err_log(dat):
    """
    Prints to the console_output with a fancy lookin error label.

    """
    s = str(dat)

    if TextReceiver.TEXT_STREAM != None:
        if len(s) > 128:
            s = s[0:128]
            print_html_to_status_bar(f'<div style="color: #e27878">[Error]</div>&nbsp;{s}...')
        else:
            print_html_to_status_bar(f'<div style="color: #e27878">[Error]</div>&nbsp;{s}')
    print("[Err] ", str(dat), file=sys.__stdout__)


def debug_log(dat):
    """    
    Writes to the status bar and to stdout

    """
    s = str(dat)
    if TextReceiver.TEXT_STREAM != None:
        if len(s) > 128:
            s = s[0:128]
            print_html_to_status_bar(f'<div style="color: #78e278">[Debug]</div>&nbsp;{s}...')
        else:
            print_html_to_status_bar(f'<div style="color: #78e278">[Debug]</div>&nbsp;{s}')
    print("[Debug] ", str(dat), file=sys.__stdout__)

