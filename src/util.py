from src.hapi import *
from src.config import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5 import uic
from time import sleep
import sys
from queue import Queue
from os import listdir

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

# Maps isotopologues text as defined by ISO in hapi to html equivalent
ISOTOPOLOGUE_NAME_TO_HTML = {}

# Maps isotopologues HTML to their local ID
ISOTOPOLOGUE_HTML_TO_GLOBAL_ID = {}

# Data scraped using the scrape.js function
# The first element in the tuple is the minimum wave number to get data, and the
# second is the maximum wave number
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

# Regex that captures a single element or isotope in a molecular composition
# This will only work for molecules in a specific format (the one found in hapi as of now).
# That is: H2O or (1H)2O
# Each isotope has it's number of neutrons before the periodic symbol, then the count of the element or isotope after
ISO_TO_HTML_REGEX = None

# Regex that captures files ending in .data, and binds everything before the .data to 'data_handle'
DATA_FILE_REGEX = re.compile('(?P<data_handle>.+)\\.data\\Z')

def print_html(html):
    global __WINDOW
    __TEXT_EDIT_STREAM.write_html(html)


# A binding to the print function that prints to stderr rather than stdout, since stdout gets redirected into a gui
# element
def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Prints to the console_output with a fancy lookin log label
def log_(dat):
    print_html('<div style="color: #7878e2">[Log]</div>&nbsp;')
    print_html(str(dat))
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


# Performas all initialization required for data structures
def util_init():
    iso_to_html_init()
    init_iso_maps()

# Performs all close operations for the util file
def util_close():
    __TEXT_RECEIVER.running = False
    print('Exiting...')
    __TEXT_THREAD.exit(0)


# Initialize maps that are constructed using data from hapi's ISO map
def init_iso_maps():
    global MOLECULE_ID_TO_ISO_COUNT
    global MOLECULE_NAME_TO_LOCAL_ID
    global MOLECULE_NAME_TO_GLOBAL_ID
    global ISOTOPOLOGUE_NAME_TO_GLOBAL_ID
    global ISOTOPOLOGUE_NAME_TO_LOCAL_ID
    global ISOTOPOLOGUE_NAME_TO_HTML
    global ISOTOPOLOGUE_HTML_TO_GLOBAL_ID

    for (k, v) in ISO.items():
        (molecule_number, isotopologue_number) = k
        if molecule_number in MOLECULE_ID_TO_ISO_COUNT:
            MOLECULE_ID_TO_ISO_COUNT[molecule_number] += 1
        else:
            MOLECULE_ID_TO_ISO_COUNT[molecule_number] = 1
        if isotopologue_number == 1:
            MOLECULE_NAME_TO_GLOBAL_ID[v[4]] = v[0]
            MOLECULE_NAME_TO_LOCAL_ID[v[4]] = molecule_number

        html = iso_to_html(v[1])
        ISOTOPOLOGUE_NAME_TO_HTML[v[1]] = html
        ISOTOPOLOGUE_HTML_TO_GLOBAL_ID[html] = v[0]

        ISOTOPOLOGUE_NAME_TO_GLOBAL_ID[v[1]] = v[0]
        ISOTOPOLOGUE_NAME_TO_LOCAL_ID[v[1]] = isotopologue_number


# Converts a molecules chemical format (e.g. H2O) to html with super and subscripts
def iso_to_html_init():
    global ISO_TO_HTML_REGEX
    # Note - this has the isotope Deuterium in it as well
    ELEMENT_REGEX = 'A[cglmrstu]|B[aehikr]?|C[adeflmnorsu]?|D[bsy]?|E[rsu]|F[elmr]?|G[ade]|H[efgos]?|I[nr]?|Kr?|L[airuv]|M[dgnot]|N[abdeiop]?|O(s)?|P[abdmortu]?|R[abefghnu]|S[bcegimnr]?|T[abcehilm]|U(u[opst])?|V|W|Xe|Yb?|Z[nr]'
    # Regex for an isotope of the form '(12C)', e.g. the number of neutrons before the element, then the periodic symbol
    ISOTOPE_REGEX = '\\((?P<neutrons>\\d+)(?P<iso_element>(' + ELEMENT_REGEX + '))\\)'
    # Regex for either an isotope or an element
    CHUNK_REGEX = '((?P<isotope>' + ISOTOPE_REGEX + ')|(?P<element>(' + ELEMENT_REGEX + ')))' + '(?P<count>\\d+)?'

    ISO_TO_HTML_REGEX = re.compile(CHUNK_REGEX)


# Converts an isotopologue in the hapi format to an HTML representation
def iso_to_html(_iso):
    iso = '%s' % _iso
    html = ''
    start = 0

    # When it's an empty string we're done
    while iso != '':
        match = ISO_TO_HTML_REGEX.match(iso)

        # Our regex didn't match - meaning the string is malformed / not a valid chemical
        if not match:
            # Special case for NOp (not sure what it is though)
            if iso == '+':
                html += iso
                return html
            print(_iso)
            print('Error parsing isotopologue to html ' + iso)
            return '<div style="color: red">Error parsing</div>'

        # Start index of our next substring (lob off the part of the string we're using now)
        start = match.end()

        # This would cause an instant crash so avoid it if possible
        if start > len(iso):
            break

        # In the regex, we defined some groups / bound some string values - this is how they get accessed
        dat = match.groupdict()
        iso = iso[start:]

        # This is an isotope - handle it as such
        if dat['neutrons'] != None:
            html += '&nbsp;<sup>' + dat['neutrons'] + '</sup>'
            html += dat['iso_element']

        # This is a regular old element
        else:
            html += dat['element']

        # How many of the element / isotope
        if dat['count'] != None:
            html += '<sub>' + dat['count'] + '</sub>'


    return html


# Returns a list of all the different data-names in the data directory
def get_all_data_names():
    files = listdir(CONFIG.data_folder)
    datas = []
    for f in files:
        match = DATA_FILE_REGEX.match(f)
        if match == None:
            continue
        datas.append(match.groupdict()['data_handle'])
    return datas

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
        self.queue.put((0, text))

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
        sleep(1)
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
    __TEXT_RECEIVER.write_text_signal.connect(main_window.console_append_text)
    __TEXT_RECEIVER.write_html_signal.connect(main_window.console_append_html)
    # Move the receiver to the background thread
    __TEXT_RECEIVER.moveToThread(__TEXT_THREAD)
    # When the thread starts, start the text receiver
    __TEXT_THREAD.started.connect(__TEXT_RECEIVER.run)
    # Start thread
    __TEXT_THREAD.start()
    # Actually link stdout with out replacement stream
    __TEXT_EDIT_STREAM.link()

