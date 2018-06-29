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

    def run(self) -> Union[bool, Tuple[type, Exception, TracebackType]]:
        result = None
        try:
            result = self.test()
        except Exception as e:
            result = sys.exc_info()
        if result == None:
            result = self.shouldFail()
        return result
