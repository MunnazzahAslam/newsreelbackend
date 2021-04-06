import json


class ErrorWrapperMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 400 <= response.status_code < 500 and hasattr(response, 'data') and response.data:
            data = {'apiError': response.data}
            json_data = json.dumps(data)
            response.content = json_data

        return response
