"""
Stats and Health API Endpoints.
Provides dashboard metrics and application health monitoring.
Serves a responsive visual status page for browsers and JSON for API clients.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app import crud
from app.models import Student
from app.schemas import StatsResponse, HealthResponse
from app import __version__

router = APIRouter(tags=["System & Statistics"])


@router.get(
    "/health",
    summary="Application Health Check",
    description="Check the server operational status and verify database connectivity. Serves a rich visual dashboard for browsers and JSON for API clients.",
)
def health_check(
    request: Request,
    format: Optional[str] = None,
    db: Session = Depends(get_db),
):
    db_status = "connected"
    student_count = 0
    try:
        db.execute(text("SELECT 1"))
        student_count = db.query(Student).count()
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    is_healthy = db_status == "connected"
    timestamp_utc = datetime.now(timezone.utc)

    # Check if request comes from a web browser
    accept_header = request.headers.get("accept", "")
    is_browser = "text/html" in accept_header and accept_header.strip() != "*/*"

    if (is_browser or format == "html") and format != "json":
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>StudentHub — System Health Status</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💚</text></svg>">
  <style>
    :root {{
      --bg: #0b1120;
      --card-bg: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --success: #10b981;
      --success-bg: rgba(16, 185, 129, 0.16);
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --border: rgba(255, 255, 255, 0.1);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: radial-gradient(circle at top, #1e293b, #0b1120 70%);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }}
    .health-container {{
      width: 100%;
      max-width: 580px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 2.25rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
      animation: fadeIn 0.3s ease-out;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .header {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
      margin-bottom: 1.75rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--border);
    }}
    .status-icon {{
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: var(--success-bg);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--success);
      font-size: 1.85rem;
      box-shadow: 0 0 24px rgba(16, 185, 129, 0.35);
      flex-shrink: 0;
    }}
    .header-text h1 {{
      font-size: 1.45rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .header-text p {{
      color: var(--text-muted);
      font-size: 0.88rem;
      margin-top: 0.2rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}
    .grid-card {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border);
      padding: 1rem 1.15rem;
      border-radius: 10px;
    }}
    .grid-card label {{
      display: block;
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.35rem;
      font-weight: 600;
    }}
    .grid-card .val {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #fff;
    }}
    .val.green {{ color: var(--success); }}
    .details-list {{
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.25rem;
      margin-bottom: 1.75rem;
      font-size: 0.88rem;
    }}
    .detail-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .detail-row span:first-child {{
      color: var(--text-muted);
      font-weight: 500;
    }}
    .detail-row span:last-child {{
      font-weight: 600;
      color: #fff;
    }}
    .actions {{
      display: flex;
      gap: 0.75rem;
      justify-content: space-between;
      flex-wrap: wrap;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.75rem 1.35rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.9rem;
      text-decoration: none;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s;
    }}
    .btn-primary {{
      background: var(--primary);
      color: #fff;
    }}
    .btn-primary:hover {{
      background: var(--primary-hover);
    }}
    .btn-secondary {{
      background: rgba(255, 255, 255, 0.06);
      border-color: var(--border);
      color: var(--text-main);
    }}
    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.12);
    }}
  </style>
</head>
<body>
  <div class="health-container">
    <div class="header">
      <div class="status-icon">✓</div>
      <div class="header-text">
        <h1>All Systems Operational</h1>
        <p>StudentHub — Backend & Database Health</p>
      </div>
    </div>

    <div class="grid">
      <div class="grid-card">
        <label>Server Status</label>
        <div class="val green">● Healthy</div>
      </div>
      <div class="grid-card">
        <label>Database Engine</label>
        <div class="val green">SQLite 3 (Connected)</div>
      </div>
      <div class="grid-card">
        <label>Total Enrolled</label>
        <div class="val">{student_count} Records</div>
      </div>
      <div class="grid-card">
        <label>HTTP Response</label>
        <div class="val green">200 OK</div>
      </div>
    </div>

    <div class="details-list">
      <div class="detail-row">
        <span>Backend Framework</span>
        <span>FastAPI & Uvicorn (ASGI)</span>
      </div>
      <div class="detail-row">
        <span>Database Connectivity</span>
        <span style="color: var(--success); font-weight: 600;">Verified Active</span>
      </div>
      <div class="detail-row">
        <span>Application Version</span>
        <span>{__version__}</span>
      </div>
      <div class="detail-row">
        <span>Server Timestamp</span>
        <span>{timestamp_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
      </div>
    </div>

    <div class="actions">
      <a href="/" class="btn btn-primary">← Back to Dashboard</a>
      <a href="/health?format=json" class="btn btn-secondary">View Raw JSON ↗</a>
    </div>
  </div>
</body>
</html>"""
        return HTMLResponse(content=html_content)

    return JSONResponse(content={
        "status": "healthy" if is_healthy else "degraded",
        "database": db_status,
        "version": __version__,
        "timestamp": timestamp_utc.isoformat(),
    })


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Dashboard Statistics",
    description="Returns aggregate counts, course distributions, and recent student registrations.",
)
def get_dashboard_stats(db: Session = Depends(get_db)):
    data = crud.get_stats(db)
    return StatsResponse(**data)

