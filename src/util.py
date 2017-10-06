from hapi import *
from PyQt4 import QtGui, uic, QtCore, Qt
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from Queue import Queue
from threading import Thread

# Maps molecule names (e.g. 'H2O') to the number of isotopologues that molecule
# has in hapi's ISO
MOLECULE_ID_TO_ISO_COUNT = {}

# Maps molecule names (e.g. 'H2O') to their molecule id (NOT the global id)
MOLECULE_NAME_TO_GLOBAL_ID = {}

# Maps molecule names (e.g. 'H2O') to their local id (that is, it's id in hapi's
# ISO)
MOLECULE_NAME_TO_LOCAL_ID = {}

# Maps isotopologue names (e.g. '(13C)(16O)2') to their global id
ISOTOPOLOGUE_NAME_TO_GLOBAL_ID = {}

# Maps isotopologue names (e.g. '(13C)(16O)2') to their local id (that is,
# it's id in hapi's ISO)
ISOTOPOLOGUE_NAME_TO_LOCAL_ID = {}

# Performas all initialization required for data structures
def util_init(*args, **kwargs):
    init_iso_maps()


# Initialize maps that are constructed using data from hapi's ISO map
def init_iso_maps():
    global MOLECULE_ID_TO_ISO_COUNT
    global MOLECULE_NAME_TO_LOCAL_ID
    global MOLECULE_NAME_TO_GLOBAL_ID
    global ISOTOPOLOGUE_NAME_TO_GLOBAL_ID
    global ISOTOPOLOGUE_NAME_TO_LOCAL_ID

    for (k, v) in ISO.iteritems():
        (molecule_number, isotopologue_number) = k
        if molecule_number in MOLECULE_ID_TO_ISO_COUNT:
            MOLECULE_ID_TO_ISO_COUNT[molecule_number] += 1
        else:
            MOLECULE_ID_TO_ISO_COUNT[molecule_number] = 1
        if isotopologue_number == 1:
            MOLECULE_NAME_TO_GLOBAL_ID[v[4]] = v[0]
            MOLECULE_NAME_TO_LOCAL_ID[v[4]] = molecule_number
        ISOTOPOLOGUE_NAME_TO_GLOBAL_ID[v[1]] = v[0]
        ISOTOPOLOGUE_NAME_TO_LOCAL_ID[v[1]] = isotopologue_number

# Attempts to convert a string to an int
# In the case of an issue or failure, it will return None
def str_to_int(s):
    try:
        x = int(s)
        return x
    except ValueError:
        return None

# A class that can be used to redirect output from stdout and stderr to a
# QTextEdit
class TextEditStream(object):
    def __init__(self):
        self.queue = Queue()

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
        self.queue.put(QString(text))

    # Clear the text area of text
    def clear(self):
        self.text_edit.clear()

# An object that will hang out in the background and receive all outputs
class TextReceiver(QObject):
    write_signal = pyqtSignal(str)

    def __init__(self, queue, *args, **kwargs):
        QObject.__init__(self)
        self.queue = queue

    @pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.write_signal.emit(text)

__TEXT_EDIT_STREAM = TextEditStream()
__TEXT_RECEIVER = None
__TEXT_THREAD = None
def init_console_redirect(main_window, *args, **kwargs):
    global __TEXT_RECEIVER
    global __TEXT_EDIT_STREAM
    global __TEXT_THREAD

    # Create a receiver
    __TEXT_RECEIVER = TextReceiver(__TEXT_EDIT_STREAM.queue, *args, **kwargs)
    # Create a thread for the receiver to run in
    __TEXT_THREAD = QThread()
    # Connect the signal to the console output handler in the main window
    __TEXT_RECEIVER.write_signal.connect(main_window.append_text)
    # Move the receiver to the background thread
    __TEXT_RECEIVER.moveToThread(__TEXT_THREAD)
    # When the thread starts, start the text receiver
    __TEXT_THREAD.started.connect(__TEXT_RECEIVER.run)
    # Start thread
    __TEXT_THREAD.start()
    # Actually link stdout with out replacement stream
    __TEXT_EDIT_STREAM.link()
