
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings
import os

def send_sms(phone, message):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False

def send_alert_email(to_email, subject, message):
    send_mail(
        subject,
        message,
        os.getenv("EMAIL_HOST_USER"),
        [to_email],
        fail_silently=False,
    )