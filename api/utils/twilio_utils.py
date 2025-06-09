# api/utils/twilio_utils.py

# from twilio.rest import Client
# from django.conf import settings

# def send_sms(to_number, message):
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#     message = client.messages.create(
#         body=message,
#         from_=settings.TWILIO_PHONE_NUMBER,
#         to=to_number
#     )
#     return message.sid




from twilio.rest import Client
from django.conf import settings

def send_sms(to_number, message):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN 

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_number
    )
    return message.sid
   
