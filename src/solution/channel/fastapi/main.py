import config as conf

from bst_core.shared.logger import get_logger

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from core.spi.db_client import DuplicationException, ForeignKeyException, NotFoundException
from solution.channel.fastapi.controller import router
from solution.channel.open_telemetry import config_open_telemetry

logger = get_logger(__name__)

app = FastAPI()
app.include_router(router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DuplicationException)
async def duplication_exception_handler(_, exc: DuplicationException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "code": status.HTTP_409_CONFLICT,
            "is_error": True,
            "message": exc.message
        },
    )


@app.exception_handler(ForeignKeyException)
async def foreign_key_exception_handler(_, exc: ForeignKeyException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": status.HTTP_400_BAD_REQUEST,
            "is_error": True,
            "message": exc.message
        },
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(_, exc: NotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "code": status.HTTP_404_NOT_FOUND,
            "is_error": True,
            "message": exc.message
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "is_error": True,
            "message": exc.detail
        },
    )


@app.exception_handler(Exception)
async def not_found_exception_handler(_, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={
                            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "is_error": True,
                            "message": "An error occurred, please read service logs"
                        },
                        )


@app.get("/health_check", tags=["utils"])
async def health_check():
    return "Ok"


if __name__ == '__main__':
    config_open_telemetry()
    uvicorn.run(
        app='solution.channel.fastapi.main:app',
        host=conf.REST_SERVER_HOST,
        port=conf.REST_SERVER_PORT,
        log_level=conf.LOGGER_LEVEL,
        reload=conf.DEBUG,
    )
