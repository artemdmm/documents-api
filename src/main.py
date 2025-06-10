from contextlib import asynccontextmanager
import uvicorn
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from fastapi import FastAPI, Request, Response
from database import init_db
from typing import Final, Callable, Awaitable, Any

from documents.router import document_router
from auth.router import auth_router
from documents.models import DocumentModel, DocTypeModel
from auth.models import UserModel, PermissionModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(document_router, prefix="/document")
app.include_router(auth_router, prefix="/auth")

class LoggingMiddleware(BaseHTTPMiddleware):
    _METADATA_FIELDS_TO_LOG: Final[set[str]] = {
        "user-id",
        "session-id",
        "external-request-id",
        "internal-request-id",
    }

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        headers = dict(request.headers)
        metadata = self._get_metadata(headers)

        if self._skip_logging_request_body(request):
            body = b""
        else:
            body = await request.body()

        with logger.contextualize(metadata=metadata):
            logger.info(
                f"Request: {request.method} {request.url}",
                headers=request.headers,
                query_params=request.query_params,
                body=body,
            )
            response = await call_next(request)

            response_raw_body = [b""]
            if hasattr(response, "body_iterator"):
                response_raw_body = [chunk async for chunk in response.body_iterator]
                response.body_iterator = iterate_in_threadpool(iter(response_raw_body))

            response_body = [content.decode("utf-8") for content in response_raw_body]

            logger.info(f"Response status: {response.status_code}", response_body=response_body)
            return response

    def _get_metadata(self, headers: dict[str, str]) -> dict[str, Any]:
        metadata = {
            key: self._kebab_to_snake(value) for key in self._METADATA_FIELDS_TO_LOG if (value := headers.get(key))
        }
        return metadata

    @staticmethod
    def _kebab_to_snake(string: str) -> str:
        return string.replace("-", "_")

    def _skip_logging_request_body(self, request: Request) -> bool:
        return bool("multipart/form-data" in request.headers.get("content-type", ""))
    
app.add_middleware(LoggingMiddleware)

if __name__  == "__main__": 
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)