import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError, HTTPException

from app.api.routers import main_router
from app.core.config import configs



logger = structlog.get_logger()
app = FastAPI(
    title=configs.PROJECT_NAME,
    openapi_url=f"{configs.API}/openapi.json",
    version="0.0.1",
)

app.add_middleware(LoggingMiddleware)
if configs.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(main_router)
#
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     body_bytes = getattr(request.state, "_body", b"")
#     request_body = parse_body(body_bytes)
#     request._body = body_bytes
#     query_params = dict(request.query_params)
#     path_params = dict(request.path_params)
#
#     logger.error(
#         "http_exception",
#         method=request.method,
#         path=request.url.path,
#         status=exc.status_code,
#         detail=exc.detail,
#         path_params=path_params or None,
#         query_params=query_params or None,
#         request_body=request_body,
#     )
#     return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
#

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     body_bytes = getattr(request.state, "_body", b"")
#     request_body = parse_body(body_bytes)
#     request._body = body_bytes
#     query_params = dict(request.query_params)
#     path_params = dict(request.path_params)
#
#     logger.warning(
#         "validation_error",
#         method=request.method,
#         path=request.url.path,
#         errors=exc.errors(),
#         path_params=path_params or None,
#         query_params=query_params or None,
#         request_body=request_body
#     )
#     return JSONResponse(status_code=422, content={"detail": exc.errors()})
#
#
# @app.exception_handler(Exception)
# async def all_exception_handler(request: Request, exc: Exception):
#     body_bytes = getattr(request.state, "_body", b"")
#     request_body = parse_body(body_bytes)
#     request._body = body_bytes
#     query_params = dict(request.query_params)
#     path_params = dict(request.path_params)
#
#     logger.exception(
#         "unhandled_exception",
#         method=request.method,
#         path=request.url.path,
#         path_params=path_params or None,
#         query_params=query_params or None,
#         request_body=request_body,
#     )
#     return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
