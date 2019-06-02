"""
This is the main module. It calls the startup functions, then runs the main-gui app
run function. Thats it.
"""
from multiprocessing import freeze_support
import sys

from startup import fix_cwd, check_version
from app import run

check_version()
fix_cwd()

if __name__ == '__main__':
    freeze_support()
    sys.exit(run())
