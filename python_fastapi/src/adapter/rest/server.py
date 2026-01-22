from os import environ
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from config.settings import settings
from config.container import container
from config.telemetry import setup_telemetry, shutdown_telemetry, instrument_app
from adapter.rest.routes import health_routes, crud_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_telemetry() # Initialize telemetry per worker
    container.initialize()
    if settings.ENVIRONMENT == "development":
        await container.db_manager().init_db()
    yield
    await container.db_manager().close_session()
    shutdown_telemetry() # Cleanup per worker

web_app = FastAPI(
    default_response_class = ORJSONResponse,
    lifespan = lifespan
    )

# Instrument FastAPI for automatic HTTP request tracing
instrument_app(web_app)

web_app.include_router(health_routes)
web_app.include_router(crud_routes)

async def start_web_server():
    await uvicorn.Server(
        uvicorn.Config(
            web_app,
            host="0.0.0.0",
            port=8080,
            workers=4, # Multiple workers
            log_level="info",
        )
    ).serve()
