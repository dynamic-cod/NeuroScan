import time
import traceback
from django.http import JsonResponse


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:  # noqa: BLE001
            duration_ms = int((time.time() - start) * 1000)
            payload = {
                "error": str(exc),
                "type": exc.__class__.__name__,
                "duration_ms": duration_ms,
            }
            traceback.print_exc()
            return JsonResponse(payload, status=500)
