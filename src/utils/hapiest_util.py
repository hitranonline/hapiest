from PyQt5.QtWidgets import *
import re
import os
from utils.config import *

# Regex that captures files ending in .data, and binds everything before the .data to 'data_handle'
DATA_FILE_REGEX = re.compile('(?P<data_handle>.+)\\.data\\Z')


# Returns a list of all the different data-names in the data directory
def get_all_data_names():
    files = os.listdir(Config.data_folder)
    datas = []
    for f in files:
        match = DATA_FILE_REGEX.match(f)
        if match == None:
            continue
        datas.append(match.groupdict()['data_handle'])
    return datas


# Used to create a map from named arguments
def echo(**kwargs):
    return kwargs
