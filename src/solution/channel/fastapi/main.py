import config as conf

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from solution.channel.fastapi.controller import router


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


@app.get("/health_check")
async def health_check():
    return "Ok"


if __name__ == '__main__':
    uvicorn.run(
        app='solution.channel.fastapi.main:app',
        host=conf.REST_SERVER_HOST,
        port=conf.REST_SERVER_PORT,
        log_level=conf.LOGGER_LEVEL,
        reload=conf.DEBUG,
    )
