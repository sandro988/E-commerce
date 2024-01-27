import random
from .models import OTP


def generate_or_update_otp(user=None):
    """
    Generate or update OTP for the given user.
    If user is not provided, only generate the OTP.
    """

    otp_code = "".join(str(random.randint(1, 9)) for _ in range(6))

    if user is not None:
        otp_entry, _ = OTP.objects.get_or_create(user=user)
        otp_entry.code = otp_code
        otp_entry.save()

    return otp_code
