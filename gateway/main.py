import src.logger_config  # noqa: F401, I001 initialize logging configuration
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.booking_proxy import router
from src.routers.desk_integration_proxy import router as desk_integration_router
from src.routers.occupancy_proxy import router as occupancy_router
from src.routers.scheduler_proxy import router as scheduler_router
from src.routers.user_proxy import router as user_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(desk_integration_router)
app.include_router(occupancy_router)
app.include_router(scheduler_router)
app.include_router(user_router)


@app.get("/")
def get_root() -> dict[str, str]:
    """Root endpoint returning a welcome message."""
    return {"message": "Welcome to the API Gateway"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
