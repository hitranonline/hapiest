import multiprocessing
from asyncio import sleep
from typing import *
from types import TracebackType
import traceback
import sys

class Test:
    def __init__(self):
        pass

    def name(self) -> str:
        return 'base test'
    
    def should_throw(self) -> bool:
        return False

    def should_fail(self) -> bool:
        return False

    def test(self) -> bool:
        return True

    def run(self, q: multiprocessing.Queue):
        def gen_tb(exc_type, exc_value, exc_traceback):
            return '\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback)).replace('\n', '\n    |   ') + '\n'

        result = None
        try:
            result = self.test()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            result = gen_tb(exc_type, exc_value, exc_traceback)
        if result == None:
            result = self.shouldFail()
        print(result)
        q.put(result)
