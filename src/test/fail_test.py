from typing import *
from .test import Test

class FailTest(Test):
    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'fail test'
    
    def shouldThrow(self) -> bool:
        return False

    def shouldFail(self) -> bool:
        return True

    def test(self) -> bool:
        return False


