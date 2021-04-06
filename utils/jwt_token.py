import jwt

from django.conf import settings
from django.utils import timezone

from utils.redis_client import redis_client

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM


def encode_token(data, expiration_time=3600, time_before=None):
    """Function that creates JWT with received date and certain expiration time."""
    try:
        if expiration_time:
            exp = int(timezone.now().timestamp()) + expiration_time
            data['exp'] = exp

        if time_before:
            nbf = int(timezone.now().timestamp()) + time_before
            data['nbf'] = nbf

        token = jwt.encode(data, JWT_SECRET, JWT_ALGORITHM)
        return token

    except TypeError:
        pass


def decode_token(token):
    """Function that handle the received JWT."""
    try:
        return jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        pass


def blacklist_token(key, exp):
    """
        ``key`` token

        ``exp`` token expiration time.

    """
    ex = exp - int(timezone.now().timestamp())
    return redis_client.set(key, 1, ex)


def is_token_blacklisted(key):
    return redis_client.get(key)
