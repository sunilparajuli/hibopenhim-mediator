import json
from .models import APILog

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only log API requests (typically starting with /api/)
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Get request body (be careful with large bodies or binary data)
        request_body = ""
        if request.body and request.content_type == 'application/json':
            try:
                request_body = request.body.decode('utf-8')
            except Exception:
                request_body = "<binary/invalid data>"

        # Get response
        response = self.get_response(request)

        # Get response body
        response_body = ""
        if response.get('Content-Type') == 'application/json':
            try:
                response_body = response.content.decode('utf-8')
            except Exception:
                response_body = "<binary/invalid data>"

        # Capture client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Log to database
        try:
            APILog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                ip_address=ip,
                request_data=request_body,
                response_data=response_body
            )
        except Exception as e:
            # Silently fail logging if database error occurs to not interrupt the service
            print(f"Logging error: {e}")

        return response
