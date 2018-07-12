from typing import *
from types import TracebackType
import traceback
import sys
import os
from utils import *
from test.test import Test
from test.fail_test import FailTest
from test.throw_test import ThrowTest
from test.hapi_sources_test import HapiSourcesTest
from test.molecule_info_test import MoleculeInfoTest
from test.graph_display_test import GraphDisplayTest
from test.band_display_test import BandDisplayTest

tests: List[Test] = [
    Test(),
    FailTest(),
    ThrowTest(),
    HapiSourcesTest(),
    MoleculeInfoTest(),
    GraphDisplayTest(),
    BandDisplayTest()
]

result_fmt = '\n{:36s} {:36s}'
name_fmt = '{:36s} '
print('{}{}'.format(name_fmt, name_fmt).format('Test Name', 'Test Result'))

def print_tb(tb):
    print('\n'.join([''] + traceback.format_tb(tb) + [str(exc_value)]).replace('\n', '\n    |   ') + '\n')

for test in tests:
    print('_' * 60)
    print(name_fmt.format(test.name()))
    result: Union[bool, Tuple[type, Exception, TracebackType]] = test.run()
    if test.should_fail():
        if result == False:
            print(result_fmt.format('', 'Ok!'))
        elif result == True:
            print(result_fmt.format('', 'Failed'))
        else:
            exc_type, exc_value, exc_traceback = result
            print(result_fmt.format('', 'Failed with exception:'))
            print_tb(exc_traceback)
    elif test.should_throw():
        if result == True:
            print(result_fmt.format('', 'Failed (should throw)'))
        elif result == False:
            print(result_fmt.format('', 'Failed (should throw)'))
        else:
            exc_type, exc_value, exc_traceback = result
            print(result_fmt.format('', 'Ok, threw:'))
            print_tb(exc_traceback)
    else:
        if result == True:
            print(result_fmt.format('', 'Ok!'))
        elif result == False:
            print(result_fmt.format('', 'Failed'))
        else:
            exc_type, exc_value, exc_traceback = result
            print(result_fmt.format('', 'Failed with exception:'))
            print_tb(exc_traceback)
