from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import settings
from .routes.weather import router as weather_router
from .routes.forecast import router as forecast_router

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(weather_router, prefix="/api/v1")
app.include_router(forecast_router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
