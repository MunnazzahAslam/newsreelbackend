from django.conf import settings

from onesignal_sdk.client import Client
from onesignal_sdk.error import OneSignalHTTPError


ONESIGNAL_APP_ID = settings.ONESIGNAL_APP_ID
ONESIGNAL_REST_API_KEY = settings.ONESIGNAL_REST_API_KEY


onesignal_client = Client(app_id=ONESIGNAL_APP_ID, rest_api_key=ONESIGNAL_REST_API_KEY)


def send_notification(notification_body):
    try:
        onesignal_client.send_notification(notification_body)
    except OneSignalHTTPError as e:
        pass
