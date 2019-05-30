from test.test import Test


class ThrowTest(Test):

    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'throw test'

    def should_throw(self) -> bool:
        return True

    def should_fail(self) -> bool:
        return False

    def test(self) -> bool:
        raise Exception('You should be seeing this.')
