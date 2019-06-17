import unittest

class TestFail(unittest.TestCase):
    def test_fail(self):
        self.assertFalse(0,1)

if __name__ == '__main__':
    unittest.main()