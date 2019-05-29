"""
This is the main module. It basically checks that there is a hapi api key, asks for one if there
is not one, and launches the main GUI. Thats about it.
"""
from multiprocessing import freeze_support
import sys

# This should be imported first: it verifies the correct python version is running, and moves the
# current working directory to wherever it ought to be. Importing things for their side-effects
# is probably bad practice, but so is using python.
from startup import fix_cwd, check_version
from app import run

check_version()
fix_cwd()

if __name__ == '__main__':
    freeze_support()
    sys.exit(run())
