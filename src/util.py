from hapi import *

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
def util_init():
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
