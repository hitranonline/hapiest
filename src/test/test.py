from typing import *
from types import TracebackType
import traceback
import sys

class Test:
    def __init__(self):
        pass

    def name(self) -> str:
        return 'base test'
    
    def shouldThrow(self) -> bool:
        return False

    def shouldFail(self) -> bool:
        return False

    def test(self) -> bool:
        return True

    def run(self) -> Union[bool, Tuple[type, Exception, TracebackType]]:
        try:
            return self.test()
        except Exception as e:
            return sys.exc_info()
