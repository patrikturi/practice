import unittest

from validation import isValidSubsequence, isValidSubsequence2, isValidSubsequence3


def make_test_case(validate):
    class MyTestCase(unittest.TestCase):
        def test_same_sequence(self):
            array = [5, 1, 22]
            sequence = [5, 1, 22]
            self.assertTrue(validate(array, sequence))

        def test_shorter_sequence_with_gap(self):
            array = [5, 1, 22]
            sequence = [5, 22]
            self.assertTrue(validate(array, sequence))

        def test_single_element_sequence(self):
            array = [5, 1, 22]
            sequence = [1]
            self.assertTrue(validate(array, sequence))

        def test_longer_sequence(self):
            array = [5, 1, 22]
            sequence = [5, 1, 22, 4]
            self.assertFalse(validate(array, sequence))

        def test_mismatched_sequence(self):
            array = [5, 1, 22]
            sequence = [5, 2]
            self.assertFalse(validate(array, sequence))

        def test_different_sequence(self):
            array = [5, 1, 22]
            sequence = [6]
            self.assertFalse(validate(array, sequence))

        def test_empty_sequence(self):
            array = [5, 1, 22]
            sequence = []
            self.assertTrue(validate(array, sequence))

        def test_empty_sequence_and_array(self):
            array = []
            sequence = []
            self.assertTrue(validate(array, sequence))

    return MyTestCase


class TestProgram(make_test_case(isValidSubsequence)):
    pass


class TestProgram2(make_test_case(isValidSubsequence2)):
    pass


class TestProgram3(make_test_case(isValidSubsequence3)):
    pass
