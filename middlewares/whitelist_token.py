import json

from django.urls import reverse
from django.http import HttpResponse

from utils.jwt_token import is_token_blacklisted


class WhiteListedTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('Authorization', '').split()
        if token and is_token_blacklisted(token[-1]):
            return HttpResponse('Token is blacklisted', status=401)

        if request.path == reverse('refresh_token'):
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return HttpResponse(status=400)

            if is_token_blacklisted(data.get('refresh')):
                return HttpResponse('Refresh token is blacklisted', status=400)

        response = self.get_response(request)
        return response
