from test.test import Test


class FailTest(Test):

    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'fail test'

    def should_throw(self) -> bool:
        return False

    def should_fail(self) -> bool:
        return True

    def test(self) -> bool:
        return False
