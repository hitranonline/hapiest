"""
This is the startup module. All of the functions here should be ran before the main app
is started.
"""
import os
import re
import sys


def check_version():
    """
    Ensures the version is at least python 3.6. The program exits if the wrong version of
    python is used.
    """
    if sys.version_info < (3, 6):
        print("You must have Python 3 installed to use hapiest, current version is " +\
                str(sys.version))
        sys.exit(0)


def fix_cwd():
    """
    If someone launches the program through the command 'python3 __main__.py', the current working
    directory is in the wrong place. This moves it to where it should be.
    """
    src_regex = re.compile('.+src\\Z')
    if src_regex.match(os.getcwd()):
        os.chdir('..')
