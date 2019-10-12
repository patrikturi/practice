from unittest import TestCase

from invalid_user_input import InvalidUserInput
from password_verifier import PasswordVerifier


# Task: https://osherove.com/tdd-kata-3
class PasswordVerifierTests(TestCase):

    def setUp(self):
        self.verifier = PasswordVerifier()

    def test_verify_passShorterThan8Chars_raisesException(self):
        self.assertRaises(InvalidUserInput, lambda: self.verifier.verify('1234567'))

    def test_verify_nonePassword_raisesException(self):
        self.assertRaises(ValueError, lambda: self.verifier.verify(None))

    def test_verify_passAllLowerCase_raisesException(self):
        self.assertRaises(InvalidUserInput, lambda: self.verifier.verify('lower0'))

    def test_verify_passAllUpperCase_raisesException(self):
        self.assertRaises(InvalidUserInput, lambda: self.verifier.verify('UPPER1'))

    def test_verify_passNoNumbers_raisesException(self):
        self.assertRaises(InvalidUserInput, lambda: self.verifier.verify('No Num'))

    def test_verify_passShorterThan8CharsButThreeOtherConditionsTrue_DoesNotRaiseException(self):
        self.verifier.verify('Short2')

    def test_verify_passAllLowerCaseButThreeOtherConditionsTrue_DoesNotRaiseException(self):
        self.verifier.verify('all lower case password 1')

    def test_verify_passNoNumbersButThreeOtherConditionsTrue_DoesNotRaiseException(self):
        self.verifier.verify('LongerThanSeverChars HasUpperAndLowerCase')

    def test_verify_passAllUpperCaseAndThreeOtherConditionsTrue_DoesNotRaiseException(self):
        self.assertRaises(InvalidUserInput, lambda: self.verifier.verify('ALL UPPER CASE PASSWORD 2'))
