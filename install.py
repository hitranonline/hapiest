#!/usr/bin/env python

import sys

if sys.version_info[0] < 3:
    print('You must have Python 3 installed to use hapiest - current version is ' + str(sys.version))
    raw_input('Hit enter to continue')
    sys.exit(0)

REQUIREMENTS = ['PyQt5', 'PyQtChart', 'toml', 'parsy']

try:
    import PyQt5
    import PyQt5.QtChart
    import toml
    import parsy

    print('All required packages are already installed!')
except:
    import os, pip

    pip_args = ['-vvv']
    if 'http_proxy' in os.environ:
        proxy = os.environ['http_proxy']
        pip_args.append('--proxy')
        pip_args.append(proxy)

    pip_args.append('install')
    for req in REQUIREMENTS:
        pip_args.append(req)
    print('Installing requirements: ' + str(REQUIREMENTS))
    pip.main(pip_args)

    try:
        import PyQt5
        import PyQt5.QtChart
        import toml
        import parsy

        print('\n\n\n\nSuccessfully installed all missing packages')
    except:
        print('Failed to install all requirements :(')
        print('Try installing the requirements manually')
        input('Hit enter to continue')
        sys.exit(0)

finally:
    from urllib.request import urlretrieve

    try:
        response = urlretrieve('https://github.com/hapiest-team/hapiest/archive/master.zip', 'hapiest.zip')
    except Exception as e:
        print('Encountered error \'' + str(e) + '\' while trying to download hapiest.')
        input('Hit enter to continue')
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
            input('Hit enter to continue')
            sys.exit(0)

input('Hit enter to continue')
