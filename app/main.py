from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.core.database import engine
from app.core.redis import get_redis, close_redis
from app.api.v1.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting Wamato API", version=settings.APP_VERSION, env=settings.ENVIRONMENT)
    await get_redis()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    await close_redis()
    await engine.dispose()
    logger.info("Wamato API shut down")


limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Uganda's Trusted Property Marketplace — REST API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# API routes
app.include_router(router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", path=request.url.path, method=request.method)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
