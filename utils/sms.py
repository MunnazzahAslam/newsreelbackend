from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from django.conf import settings


account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN

try:
    client = Client(account_sid, auth_token)
except TwilioException:
    pass


def send_sms(message, phone_number):
    try:
        response = client.messages.create(
            body=message,
            from_='+15672293739',
            to=phone_number
        )

        return not response.error_code
    except Exception:
        pass
