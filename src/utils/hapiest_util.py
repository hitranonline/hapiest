import os
import re

from PyQt5.QtGui import QIcon

from utils.metadata.config import *

# Regex that captures files ending in .data, and binds everything before the .data to 'data_handle'
DATA_FILE_REGEX = re.compile('(?P<data_handle>.+)\\.(data|par|xsc)\\Z')

VERSION_STRING = "v0.1a"

ICON = None
def program_icon():
    global ICON
    if ICON is None:
        ICON = QIcon("res/img/icons/icon.png")
    return ICON

def get_all_data_names():
    """
    Returns a list of all the different data-names in the data directory.

    :returns: A set of all of the data names in the data folders

    """
    files = os.listdir(Config.data_folder)
    datas = []
    for f in files:
        match = DATA_FILE_REGEX.match(f)
        if match == None:
            continue
        if f.endswith('.xsc'):
            datas.append(match.string)
        else:
            datas.append(match.groupdict()['data_handle'])
    return list(set(datas))

# Regex that captures files ending in .data, and binds everything before the .data to 'data_handle'
JSON_FILE_REGEX = re.compile('(?P<data_handle>.+)\\.json\\Z')


def echo(**kwargs):
    """
    :param kwargs the keyworded arguments
    :returns: the dictionary kwargs

    """
    return kwargs
