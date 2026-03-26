from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import config
from routers import carbon_intensity, octopus

limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

app = FastAPI(
    title="Energy Dashboard API",
    version="v1",
    description="This is the documentation for the Energy Dashboard API",
    docs_url="/docs/swagger",
    redoc_url="/docs/",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if config.DEVELOPMENT:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
def health():
    return PlainTextResponse("ok")


@app.get("/", response_class=HTMLResponse)
def root():
    return (
        '<div style="max-width: 400px;font-family: Helvetica, Sans-Serif;'
        'font-size: 1.2em;margin: 20vh auto;">'
        '<p>"<strong>200 OK.</strong> Welcome to the Energy Dashboard API."</p>'
        "</div>"
    )


app.include_router(carbon_intensity.router, prefix="/api/v1")
app.include_router(octopus.router, prefix="/api/v1")
