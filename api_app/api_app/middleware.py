class RemoveDRFLinkHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Remove 'Link' header if it exists
        response.headers.pop('Link', None)

        return response