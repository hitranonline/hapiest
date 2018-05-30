from typing import *
from types import TracebackType
import traceback
import sys
import os
from ..utils import *
from .test import Test
from .fail_test import FailTest
from .throw_test import ThrowTest


tests: List[Test] = [Test(), FailTest(), ThrowTest()]

result_fmt = '{:18s}'
name_fmt = '{:16s} '
print('{}{}'.format(name_fmt, result_fmt).format('Test Name', 'Test Result'))

for test in tests:
    print(name_fmt.format(test.name()), end='')
    
    result: Union[bool, Tuple[type, Exception, TracebackType]] = test.run()
    if test.shouldFail():
        if result == False:
            print('Ok!')
        elif t == True:
            print(result_fmt.format('Failed'))
        else:
            exc_type, exc_value, exc_traceback = result
            print(result_fmt.format('Failed with exception:'))
            print('\n'.join([''] + traceback.format_tb(exc_traceback)).replace('\n', '\n        '))
    elif test.shouldThrow():
        if result == True:
            print(result_fmt.format('Failed (should throw)'))
        elif result == False:
            print(result_fmt.format('Failed (should throw)'))
        else:
            exc_type, exc_value, exc_traceback = result
            print(result_fmt.format('Ok, threw:'))
            print('\n'.join([''] + traceback.format_tb(exc_traceback)).replace('\n', '\n        '))
    else:
        if result == True:
            print('Ok!')
        elif result == False:
            print(result_fmt.format('Failed'))
        else:
            exc_type, exc_value, exc_traceback = result
            print(result_fmt.format('Failed with exception:'))
            print('\n'.join([''] + traceback.format_tb(exc_traceback)).replace('\n', '\n        '))
