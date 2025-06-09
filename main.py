from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from routes.documents import document_router
from routes.users import user_router
from database.connection import init_db
from models.documents import DocumentModel
from models.users import UserModel
from models.permissions import PermissionModel
from models.document_type import DocTypeModel
from models.logs import ApiLog
from utils.logging import write_log

import uvicorn
from time import perf_counter
from starlette.concurrency import iterate_in_threadpool
from starlette.background import BackgroundTask

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(document_router, prefix="/document")
app.include_router(user_router, prefix="/user")

@app.middleware("http")
async def middleware(request: Request, call_next):
    try:
        req_body = await request.json()
    except Exception:
        req_body = None

    start_time = perf_counter()
    response = await call_next(request)
    process_time = perf_counter() - start_time

    res_body = [section async for section in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(res_body))
    res_body = res_body[0].decode()
    
    response.background = BackgroundTask(write_log, request, response, req_body, res_body, process_time)
    return response

if __name__  == "__main__": 
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)