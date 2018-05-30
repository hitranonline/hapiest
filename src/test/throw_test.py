from typing import *
from .test import Test

class ThrowTest(Test):
    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'base test'
    
    def shouldThrow(self) -> bool:
        return True

    def shouldFail(self) -> bool:
        return False

    def test(self) -> bool:
        raise Exception('You should be seeing this.')
