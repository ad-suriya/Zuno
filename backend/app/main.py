import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, media
from app.api.routes import router
from app.config import get_settings
from app.errors import error_response, register_error_handlers
from app.logging_config import configure_logging

REQUEST_ID_HEADER = "X-Request-ID"

log = logging.getLogger("zuno.errors")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(json_output=settings.on_cloud_run)

    app = FastAPI(title="Zuno API", version=health.VERSION)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        rid = (request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex)[:64]
        request.state.request_id = rid
        try:
            response = await call_next(request)
        except Exception as exc:
            # Handled here (not by an Exception handler) so the response still passes through CORS.
            log.error("unhandled_error", exc_info=exc, extra={"request_id": rid})
            response = error_response(request, 500, "INTERNAL_ERROR", "Something went wrong on our side.")
        response.headers[REQUEST_ID_HEADER] = rid
        return response

    # Added last so it is the outermost middleware and wraps error responses too.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", REQUEST_ID_HEADER],
        expose_headers=[REQUEST_ID_HEADER],
    )

    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(router)
    app.include_router(media.router)
    return app


app = create_app()
