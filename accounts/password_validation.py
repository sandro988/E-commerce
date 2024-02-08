from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import string


class OnlyAlphabeticPasswordValidator:
    """
    Validator to ensure the password does not consist only of alphabetic characters.
    """

    def validate(self, password, user=None):
        if password.isalpha():
            raise ValidationError(
                _("The password cannot consist only of alphabetic characters."),
                code="password_entirely_alpha",
            )

    def get_help_text(self):
        return _("Your password must contain at least one non-alphabetic character.")


class OnlySpecialCharactersPasswordValidator:
    """
    Validator to ensure the password does not consist only of special characters.
    """

    def validate(self, password, user=None):
        if all(char in string.punctuation for char in password):
            raise ValidationError(
                _("The password cannot consist only of special characters."),
                code="password_entirely_special_chars",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one non-special character (alphabetic or numeric)."
        )
