import unittest


class TrivialFailures(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(1, 1)

    def test_fail(self):
        self.fail()

    def test_error(self):
        raise RuntimeError("This is an error")
