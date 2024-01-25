import random
from django.core.mail import EmailMessage
from django.conf import settings
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


def send_one_time_password_to_user(user):
    otp_code = generate_or_update_otp(user)
    subject = "One time code for account verification."
    email_body = otp_code
    from_email = settings.DEFAULT_FROM_EMAIL

    email = EmailMessage(
        subject=subject, body=email_body, from_email=from_email, to=[user.email]
    )
    email.send()

    return user
