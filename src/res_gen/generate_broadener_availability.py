"""
When you download data from HITRAN, but HITRAN does not have data for a specific line, a '#' is put
in place. This seems to only apply to "Extra" parameters, which are appended to the end of the
standard 160 character lines in a comma separated manner.

This is a script that
1. downloads data for every molecule in hitran with line by line data available, and requests
    extra broadener related parameters
2. checks to see if the extra parameters are actually populated (i.e. not empty)
3. Creates a JSON file that contains a key for each molecule (by ID), and the value is a set
    of the extra broadeners that it actually has data for.

Current possible issues:
- Only check the first line of data. The holes in the data may only be for the first few lines.
- this code sucks
"""

import json
import sys
import traceback

import hapi
from metadata.config import Config
from metadata.isotopologue_meta import IsotopologueMeta
from metadata.molecule_meta import MoleculeMeta
from metadata.table_header import TableHeader

PARAMETERS = hapi.PARLIST_ALL
params = list(PARAMETERS) + hapi.PARLIST_DOTPAR


def check_availability(molecule: MoleculeMeta, numin=2000, numax=2050):
    available_params = []
    
    for i in [".par", "160-char", "par_line"]:
        available_params.append(i)

    print(available_params)

    for param in params:
        try:
            iso = IsotopologueMeta.from_molecule_id(molecule.id)
            print(f"Trying to fetch {param} for {iso.iso_name} {numin}-{numax}")
            
            hapi.fetch_by_ids("TempTable", [iso.id], numin=numin,numax=numax, Parameters=["par_line", param])
            
            table_header = TableHeader("TempTable")
            
            with open("__temp_data/TempTable.data") as f:
                line = f.readline()
    
            segments = line.split(',')
            if len(segments) == 1:
                print(segments)
                continue
            segments = segments[1:]
            print(segments)
            assert len(segments) == 1
            if "#" not in segments[0]:
                available_params.append(param)
                assert table_header.extra[0] == param
                print("ADDED " + param)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)
            pass

    return list(set(available_params))

def generate_availability():
    try:
        generate_availability_()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)


def generate_availability_():
    Config.data_folder = "__temp_data"
    hapi.db_begin(Config.data_folder)

    records = dict()
    for molecule_id in range(0, 100):
        molecule = MoleculeMeta(molecule_id)
        if not molecule.is_populated():
            continue
        records[molecule.id] = check_availability(molecule)

    with open(f"res/parameters/availability.json", "w+") as f:
        f.write(json.dumps(records, indent=2, sort_keys=True))

    print(records)

    sys.exit(0)
