from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
import time

REQUEST_COUNT = Counter(
    "wc_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "wc_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        resp_time = time.time() - start
        endpoint = request.url.path
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(resp_time)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=str(response.status_code)).inc()
        return response


def metrics_endpoint() -> Response:
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


def mount_metrics(app: FastAPI, path: str = "/metrics"):
    @app.get(path)
    def _metrics():
        return metrics_endpoint()
