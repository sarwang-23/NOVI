import uuid
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict

# Very simple in-memory rate limiter for MVP (Tokens bucket per IP)
# In production, replace with Redis
RATE_LIMIT_DATA = defaultdict(lambda: {"tokens": 100, "last_refill": time.time()})
RATE_LIMIT_CAPACITY = 100
RATE_LIMIT_REFILL_RATE = 10 # tokens per second

class EnterpriseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1. Request ID Injection
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # 2. Simple Rate Limiting (by IP)
        client_ip = request.client.host if request.client else "unknown"
        
        now = time.time()
        bucket = RATE_LIMIT_DATA[client_ip]
        
        # Refill tokens
        time_passed = now - bucket["last_refill"]
        bucket["tokens"] = min(RATE_LIMIT_CAPACITY, bucket["tokens"] + time_passed * RATE_LIMIT_REFILL_RATE)
        bucket["last_refill"] = now
        
        # We don't rate limit the health check endpoints
        if not request.url.path.startswith("/health"):
            if bucket["tokens"] < 1.0:
                return Response(content="Rate limit exceeded", status_code=429)
            
            bucket["tokens"] -= 1.0

        # Process the request
        response = await call_next(request)
        
        # Return request ID in header
        response.headers["X-Request-ID"] = request_id
        
        return response
