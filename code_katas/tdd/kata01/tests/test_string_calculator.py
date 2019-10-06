import unittest

from string_calculator import StringCalculator


class TestStringCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = StringCalculator()

    def test_add_emptyString_returnsZero(self):
        self.assertEqual(0, self.calc.add(''))

    def test_add_singleNumber_returnsSameNumber(self):
        self.assertEqual(5, self.calc.add('5'))

    def test_add_twoNumbers_returnsSum(self):
        self.assertEqual(7, self.calc.add('2,5'))

    def test_add_fourNumbers_returnsSum(self):
        self.assertEqual(20, self.calc.add('3,7,9,1'))

    def test_add_threeNumbersWithNewline_returnsSum(self):
        self.assertEqual(8, self.calc.add('2\n5,1'))

    def test_add_customDelimiter_returnsSum(self):
        self.assertEqual(8, self.calc.add('//;\n2;1;5'))

    def test_add_negativeNumber_raisesException(self):
        self.assertRaisesRegex(ValueError, 'negatives not allowed', lambda: self.calc.add('1,-1'))

    def test_add_numberLargerThan1000_returnsSumLargeNumberIgnored(self):
        self.assertEqual(2, self.calc.add('2,1001'))

    def test_add_multiCharDelimiter_returnsSum(self):
        self.assertEqual(6, self.calc.add('//[***]\n1***2***3'))

    def test_add_multipleDelimiters_returnsSum(self):
        self.assertEqual(6, self.calc.add('//[*][%]\n1*2%3'))

    def test_add_multipleDelimitersMultiChar_returnsSum(self):
        self.assertEqual(6, self.calc.add('//[*][%%]\n1*2%%3'))
