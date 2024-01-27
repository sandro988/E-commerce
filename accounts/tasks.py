from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .utils import generate_or_update_otp
from .models import CustomUser, OTP


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


@shared_task
def delete_expired_otps():
    expired_otps = OTP.objects.filter(expiry_timestamp__lte=timezone.now())
    expired_otps.delete()


@shared_task
def send_password_reset_email_task(
    subject,
    email_template_name,
    context,
    from_email,
    to_email,
    html_email_template_name=None,
):
    # Getting the user instance with email received in context.
    user = CustomUser.objects.get(email=context["user"])
    context["user"] = user
    subject = render_to_string(subject, context).strip()
    body = render_to_string(email_template_name, context)
    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])

    if html_email_template_name:
        html_email = render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, "text/html")

    email_message.send()


@shared_task
def send_already_verified_email(user_email):
    subject = "Account Verification Reminder"
    context = {
        "user_email": user_email,
    }
    email_body = render_to_string("already_verified_email_template.html", context)

    email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )
    email.send()
