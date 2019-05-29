import os
import re
import sys

if sys.version_info < (3, 6):
    print(f"You must have Python 3 installed to use hapiest, current version is {str(sys.version)}")
    sys.exit(0)

# If someone launches the program through the command 'python3 __main__.py'
# this moves the current working directory to the proper place
srcre = re.compile('.+src\\Z')
if srcre.match(os.getcwd()):
    os.chdir('..')



