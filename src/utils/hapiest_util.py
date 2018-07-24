import re
import os
from utils.metadata.config import *

# Regex that captures files ending in .data, and binds everything before the .data to 'data_handle'
DATA_FILE_REGEX = re.compile('(?P<data_handle>.+)\\.(data|par)\\Z')



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
        datas.append(match.groupdict()['data_handle'])
    return list(set(datas))

# Regex that captures files ending in .data, and binds everything before the .data to 'data_handle'
JSON_FILE_REGEX = re.compile('(?P<data_handle>.+)\\.json\\Z')



def get_all_json_molecule_names():
    """
    :returns: a list of all the molecules that have JSON corresponding to them.
    """
    files = os.listdir('res/molecules/')
    datas = []
    for f in files:
        match = JSON_FILE_REGEX.match(f)
        if match == None:
            continue
        datas.append(match.groupdict()['data_handle'])
    return list(set(datas))



def echo(**kwargs):
    """
    :param kwargs the keyworded arguments
    :returns: the dictionary kwargs

    """
    return kwargs
