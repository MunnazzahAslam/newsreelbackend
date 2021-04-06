import redis

from django.conf import settings

REDIS_URL = settings.REDIS_URL

try:
    redis_client = redis.Redis.from_url(REDIS_URL)
except ValueError:
    redis_client = None
