from hapi import *
from config import *
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

# The program config object
CONFIG = Configuration()

# Data scraped using the scrape.js function
MOLECULE_DATA_RANGE = {
    1    :    (8.400e-5, 25710.825),
    2    :    (0.757, 14075.298),
    3    :    (0.026, 6996.681),
    4    :    (0.791, 10363.675),
    5    :    (3.402, 14477.377),
    6    :    (0.001, 11501.872),
    7    :    (6.440e-7, 17272.060),
    8    :    (1.000e-6, 9273.214),
    9    :    (0.017, 4092.948),
    10    :    (0.498, 3074.153),
    11    :    (0.058, 10348.719),
    12    :    (0.007, 1769.982),
    13    :    (0.003, 35874.955),
    14    :    (13.620, 32351.592),
    15    :    (5.342, 20231.245),
    16    :    (7.656, 16033.492),
    17    :    (5.888, 13907.689),
    18    :    (0.015, 1207.639),
    19    :    (0.396, 7821.109),
    20    :    (1.000e-6, 3099.958),
    21    :    (1.081, 3799.682),
    22    :    (11.541, 9354.200),
    23    :    (0.015, 17585.789),
    24    :    (0.873, 3197.961),
    25    :    (0.043, 1730.371),
    26    :    (1.983, 9889.038),
    27    :    (225.045, 3000.486),
    28    :    (1.901e-6, 3601.652),
    29    :    (686.731, 2001.348),
    30    :    (580.000, 996.000),
    31    :    (2.985, 11329.780),
    32    :    (10.018, 1889.334),
    33    :    (0.173, 3675.819),
    34    :    (68.716, 158.303),
    35    :    (763.641, 797.741),
    36    :    (3.976, 2530.462),
    37    :    (0.155, 315.908),
    38    :    (614.740, 3242.172),
    39    :    (0.019, 1407.206),
    40    :    (794.403, 1705.612),
    41    :    (890.052, 945.665),
    42    :    (582.830, 1518.016),
    43    :    (0.053, 1302.217),
    44    :    (4.360e-4, 759.989),
    45    :    (3.227, 36405.367),
    46    :    (1.532, 2585.247),
    47    :    (0.040, 2824.347),
    48    :    (200.772, 307.374),
    49    :    (793.149, 899.767)
}

# Performas all initialization required for data structures
def util_init(*args, **kwargs):
    init_iso_maps()

def util_close():
    __TEXT_RECEIVER.running = False
    print 'Exiting...'
    __TEXT_THREAD.exit(0)

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
        self.running = True

    @pyqtSlot()
    def run(self):
        while self.running:
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
