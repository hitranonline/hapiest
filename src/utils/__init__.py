import re
DATA_FILE_REGEX = re.compile('(?P<data_handle>.+)\\.data\\Z')
def get_all_data_names():
    """
    Returns a list of all the different data-names in the data directory.
    """
    files = listdir(Config.data_folder)
    datas = []
    for f in files:
        match = FetchHandler.DATA_FILE_REGEX.match(f)
        if match == None:
            continue
        datas.append(match.groupdict()['data_handle'])
    return datas
