import time
from collections import defaultdict, deque
from django.http import JsonResponse


class RateLimiterMiddleware:
    def __init__(self, get_response, max_requests=60, window_seconds=60):
        self.get_response = get_response
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.client_requests = defaultdict(deque)

    def __call__(self, request):
        client_ip = request.META.get("REMOTE_ADDR", "unknown")
        now = time.time()
        window = self.client_requests[client_ip]

        while window and now - window[0] > self.window_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            return JsonResponse({"error": "rate_limit_exceeded"}, status=429)

        window.append(now)
        return self.get_response(request)
