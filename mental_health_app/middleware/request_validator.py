from django.http import JsonResponse


class RequestValidatorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Example validation: Enforce JSON for API endpoints
        if request.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH"}:
            content_type = request.META.get("CONTENT_TYPE", "")
            if "application/json" not in content_type:
                return JsonResponse({"error": "invalid_content_type"}, status=400)
        return self.get_response(request)
