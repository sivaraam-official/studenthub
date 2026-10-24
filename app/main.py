"""
FastAPI Main Application.
Mounts routers, configures CORS, handles lifecycle startup events,
and serves the frontend dashboard.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database import engine, Base, SessionLocal
from app.routers import students, stats
from app.crud import seed_initial_data_if_empty
from app import __version__

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: initialize database tables and seed sample records on startup.
    """
    # Create all database tables
    Base.metadata.create_all(bind=engine)

    # Seed sample fictional data if empty for immediate live demo
    db = SessionLocal()
    try:
        seed_initial_data_if_empty(db)
    finally:
        db.close()

    yield
    # Shutdown logic (if any)


# Initialize FastAPI application
app = FastAPI(
    title="StudentHub API",
    description=(
        "Student Database Management System REST API built for EWB Edu Tech Internship Assignment. "
        "Provides full CRUD operations, pagination, search, dashboard stats, and health monitoring."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
# Allows requests from local frontend dev servers or separate domains
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom Validation Error Handler for beginner-friendly errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": field,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "errors": errors,
        },
    )


# Custom 500 error handler to prevent leakage of internal server details
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # In production, log the error and return a safe message
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please check server logs or try again.",
        },
    )


# Include API routers (both at root level and /api prefix for flexibility)
app.include_router(students.router)
app.include_router(stats.router)

# Also expose under /api for standardized frontend routing
api_router = FastAPI()
api_router.include_router(students.router)
api_router.include_router(stats.router)
app.mount("/api", api_router)

# Mount frontend static directory if exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Welcome to StudentHub API. Visit /docs for Swagger documentation."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
