import time
from django.utils.deprecation import MiddlewareMixin
from ..models import APIMetric


class RequestMetricsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        try:
            start = getattr(request, "_start_time", None)
            if start is not None:
                latency_ms = int((time.time() - start) * 1000)
                APIMetric.objects.create(
                    endpoint=request.path,
                    method=request.method,
                    status_code=getattr(response, "status_code", 0),
                    latency_ms=latency_ms,
                )
        except Exception:
            pass
        return response
