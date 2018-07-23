import multiprocessing
from multiprocessing import Process, freeze_support
from time import sleep
from typing import *
from types import TracebackType
from threading import *
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
from test.config_editor_test import ConfigEditorTest

tests: List[Test] = [
    Test(),
    FailTest(),
    ThrowTest(),
    HapiSourcesTest(),
    MoleculeInfoTest(),
    GraphDisplayTest(),
    BandDisplayTest(),
    ConfigEditorTest()
]

def run_tests():
    result_fmt = '\n{:36s} {:36s}'
    name_fmt = '{:36s} '
    print('{}{}'.format(name_fmt, name_fmt).format('Test Name', 'Test Result'))
    print('NAME: ' + __name__)

    q = multiprocessing.Queue()
    for test in tests:
        print('_' * 60)
        print(name_fmt.format(test.name()))
        p = Process(target=test.run, args=(q,))
        p.start()
        p.join()
        result: Union[bool, Tuple[type, Exception, TracebackType]] = q.get()
        if test.should_fail():
            if result == False:
                print(result_fmt.format('', 'Ok!'))
            elif result == True:
                print(result_fmt.format('', 'Failed'))
            else:
                traceback = result
                print(result_fmt.format('', 'Failed with exception:'))
                print(traceback)
        elif test.should_throw():
            if result == True:
                print(result_fmt.format('', 'Failed (should throw)'))
            elif result == False:
                print(result_fmt.format('', 'Failed (should throw)'))
            else:
                traceback = result
                print(result_fmt.format('', 'Failed with exception:'))
                print(traceback)
        else:
            if result == True:
                print(result_fmt.format('', 'Ok!'))
            elif result == False:
                print(result_fmt.format('', 'Failed'))
            else:
                traceback = result
                print(result_fmt.format('', 'Failed with exception:'))
                print(traceback)
