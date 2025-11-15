import json
import structlog
from urllib.parse import parse_qs
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


def parse_body(body: bytes):
    if not body:
        return None

    text = None
    try:
        text = body.decode("utf-8")
    except Exception:
        return {"raw": "<binary>"}

    # Попытка JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    try:
        parsed = parse_qs(text, keep_blank_values=True)
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    except Exception:
        pass

    # fallback
    return {"raw": text}


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        raw = await request.body()
        body_bytes = bytes(raw)
        request_body = parse_body(body_bytes)
        request.state._body = body_bytes

        query_params = dict(request.query_params)
        path_params = dict(request.path_params)

        response = await call_next(request)

        response_body = None
        if isinstance(response, JSONResponse):
            response_body = parse_body(bytes(response.body))

        if request.url.path == "/metrics":
            return response

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            path_params=path_params or None,
            query_params=query_params or None,
            request_body=request_body,
            response_body=response_body,
        )

        return response
