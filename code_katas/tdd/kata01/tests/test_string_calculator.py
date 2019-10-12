import unittest
from unittest.mock import Mock

from string_calculator import StringCalculator


# Task part 1: https://osherove.com/tdd-kata-1
# part 2: https://osherove.com/tdd-kata-2
class TestStringCalculator(unittest.TestCase):

    def setUp(self):
        self.logger = Mock(spec_set=['write'])
        self.webservice = Mock(spec_set=['logging_failed'])
        self.calc = StringCalculator(self.logger, self.webservice)

        self.valid_input = '1,2'
        self.sum_of_valid_input = 3

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

    def test_add_validInput_logsResult(self):
        self.calc.add(self.valid_input)
        self.logger.write.assert_called_with('{}\n'.format(self.sum_of_valid_input))

    def test_add_loggerRaisesException_notifiesWebservice(self):
        logging_error_message = 'Logging failed'
        self.logger.write.side_effect = RuntimeError(logging_error_message)
        self.calc.add(self.valid_input)
        self.webservice.logging_failed.assert_called_with(logging_error_message)
