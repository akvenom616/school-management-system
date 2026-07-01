from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .validators import ComplexPasswordValidator


class PasswordValidatorTests(SimpleTestCase):
    def setUp(self):
        self.validator = ComplexPasswordValidator()

    def test_rejects_password_without_required_complexity(self):
        with self.assertRaises(ValidationError):
            self.validator.validate('abcdefghij')

    def test_rejects_password_outside_length_range(self):
        with self.assertRaises(ValidationError):
            self.validator.validate('Abc1!xyz')

    def test_accepts_a_strong_password(self):
        self.validator.validate('Abc12!wxyz')
