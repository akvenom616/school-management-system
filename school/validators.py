import re

from django.core.exceptions import ValidationError


class ComplexPasswordValidator:
    """Enforce a strong password policy for accounts."""

    def __init__(self, min_length=10, max_length=12):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password, user=None):
        if not isinstance(password, str):
            raise ValidationError('Password must be a string.')

        if not (self.min_length <= len(password) <= self.max_length):
            raise ValidationError(
                f'Password must be between {self.min_length} and {self.max_length} characters long.'
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')

        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')

        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')

        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValidationError('Password must contain at least one special character.')

    def get_help_text(self):
        return (
            'Password must be 10-12 characters long and include an uppercase letter, '
            'a lowercase letter, a number, and a special character.'
        )
