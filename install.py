#!/usr/bin/env python

import sys

if sys.version < (3, 6):
    print(sys.version_info[0])
    print('You must have Python 3 installed to use hapiest - current version is ' + str(sys.version))
    sys.exit(0)

## Dependencies required to install
REQUIREMENTS = ['PyQt5', 'PyQtChart', 'toml', 'parsy']

try:
    import PyQt5
    import PyQt5.QtChart
    import toml
    import parsy

    print('All required packages are already installed!')
except Exception as e:
    print("Missing dependency:\n" + str(e))

finally:
    from urllib.request import urlretrieve

    try:
        response = urlretrieve('https://github.com/hitranonline/hapiest/archive/master.zip', 'hapiest.zip')
    except Exception as e:
        print('Encountered error \'' + str(e) + '\' while trying to download hapiest.')
        sys.exit(0)
    finally:
        import zipfile

        try:
            zip = zipfile.ZipFile('hapiest.zip', 'r')
            zip.extractall('hapiest')
            zip.close()
            print('Hapiest has successfully been installed in the directory \'hapiest\'')
        except Exception as e:
            print('Encountered error \'' + str(e) + '\' when attempting to extract hapiest.zip')
            sys.exit(0)
