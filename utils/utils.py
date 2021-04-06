from django.utils.crypto import get_random_string

from .sms import send_sms
from users.models import PhoneVerification


def generate_and_send_phone_verification_number_code(user):
    code = get_random_string(length=6, allowed_chars='0123456789')
    PhoneVerification.objects.create(code=code, user=user)
    message = 'Your NewsReel verification code is: %s' % code
    return send_sms(message, user.phone_number.as_international)
