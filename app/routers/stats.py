"""
Stats and Health API Endpoints.
Provides dashboard metrics and application health monitoring.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app import crud
from app.schemas import StatsResponse, HealthResponse
from app import __version__

router = APIRouter(tags=["System & Statistics"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
    description="Check the server operational status and verify database connectivity.",
)
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        # Execute a quick lightweight check
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        version=__version__,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Dashboard Statistics",
    description="Returns aggregate counts, course distributions, and recent student registrations.",
)
def get_dashboard_stats(db: Session = Depends(get_db)):
    data = crud.get_stats(db)
    return StatsResponse(**data)
