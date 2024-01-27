from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from .utils import generate_or_update_otp
from .models import CustomUser


@shared_task
def send_one_time_password_to_user(user_id):
    user = CustomUser.objects.get(pk=user_id)
    otp_code = generate_or_update_otp(user)
    subject = "One time code for account verification."
    email_body = otp_code
    from_email = settings.DEFAULT_FROM_EMAIL

    email = EmailMessage(
        subject=subject, body=email_body, from_email=from_email, to=[user.email]
    )
    email.send()
