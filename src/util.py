from hapi import * #edited src.
from config import * #edited src.
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5 import uic
from time import sleep
import sys
from queue import Queue
from os import listdir

# Regex that captures files ending in .data, and binds everything before the .data to 'data_handle'

def print_html(*args):
    global __WINDOW
    for arg in args:
        __TEXT_EDIT_STREAM.write_html(args)


# A binding to the print function that prints to stderr rather than stdout, since stdout gets redirected into a gui
# element
def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Prints to the console_output with a fancy lookin log label
def log_(*args):
    print_html('<div style="color: #7878e2">[Log]</div>&nbsp;')
    print_html(*args)
    print_html('<br>')


# Prints to the console_output with a fancy lookin error label
def err_(dat):
    print_html('<div style="color: #e27878">[Error]</div>&nbsp;')
    print_html(str(dat))
    print_html('<br>')


def debug_(dat):
    print_html('<div style="color: #78e278">[Debug]</div>&nbsp;')
    print_html(str(dat))
    print_html('<br>')

# Performs all close operations for the util file
def util_close():
    __TEXT_RECEIVER.running = False
    print('Exiting...')
    __TEXT_THREAD.exit(0)

# Attempts to convert a string to an int
# In the case of an issue or failure, it will return None
def str_to_int(s):
    try:
        x = int(s)
        return x
    except ValueError:
        return None


# Attempts to convert a string to an int
# In the case of an issue or failure, it will return None
def str_to_float(s):
    try:
        x = int(s)
        return x
    except ValueError:
        return None


# A class that can be used to redirect output from stdout and stderr to a
# QTextEdit
class TextEditStream(object):
    def __init__(self, window):
        self.queue = Queue()
        self.window = window

    # Link this object to stdout
    def link(self):
        sys.stdout = self


    # Restore stdout back to normal console output
    def restore(self):
        sys.stdout = sys.__stdout__


    # Append text to the text_edit
    # To handle multiple threads attempting to write at once, add very simple
    # semaphore-type usage checking / waiting
    def write(self, text):
        self.queue.put((0, str(text)))

    # Similar to the write method, but pass a 1 instead of a zero, indicating that the text is html rather than normal text
    def write_html(self, html):
        self.queue.put((1, html))

    def flush(self):
        pass

    # Clear the text area of text
    def clear(self):
        self.text_edit.clear()


# An object that will hang out in the background and receive all outputs
class TextReceiver(Qt.QObject):
    write_text_signal = QtCore.pyqtSignal(str)
    write_html_signal = QtCore.pyqtSignal(str)

    def __init__(self, queue, *args, **kwargs):
        Qt.QObject.__init__(self)
        self.queue = queue
        self.running = True


    def run(self):
        while self.running:
            (ty, text) = self.queue.get()
            if ty == 0:
                self.write_text_signal.emit(text)
            else:
                self.write_html_signal.emit(text)


__TEXT_EDIT_STREAM = None
__TEXT_RECEIVER = None
__TEXT_THREAD = None
__WINDOW = None

def init_console_redirect(main_window, *args, **kwargs):
    global __TEXT_RECEIVER
    global __TEXT_EDIT_STREAM
    global __TEXT_THREAD
    global __WINDOW

    __TEXT_EDIT_STREAM = TextEditStream(main_window)

    __WINDOW = main_window
    # Create a receiver
    __TEXT_RECEIVER = TextReceiver(__TEXT_EDIT_STREAM.queue, *args, **kwargs)
    # Create a thread for the receiver to run in
    __TEXT_THREAD = QtCore.QThread()
    # Connect the signal to the console output handler in the main window
    # Connect the console output signals
    __TEXT_RECEIVER.write_text_signal.connect(lambda str: main_window.console_append_text(str))
    __TEXT_RECEIVER.write_html_signal.connect(lambda html: main_window.console_append_html(html))
    # Move the receiver to the background thread
    __TEXT_RECEIVER.moveToThread(__TEXT_THREAD)
    # When the thread starts, start the text receiver
    __TEXT_THREAD.started.connect(__TEXT_RECEIVER.run)
    # Start thread
    __TEXT_THREAD.start()
    # Actually link stdout with out replacement stream
    __TEXT_EDIT_STREAM.link()
