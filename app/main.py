"""Main FastAPI Application for Taller 3 - Modo Oscuro Dashboard."""
from pathlib import Path
from typing import Optional, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from app.config import settings
from app.feature_flags import feature_flag_service

# Paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# In-memory storage for user preferences (Ticket 3 Backend persistence)
USER_PREFERENCES: Dict[str, str] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    yield
    feature_flag_service.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Static and Templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# -------------------------------------------------------------------------
# Request Models
# -------------------------------------------------------------------------
class UserPreferenceRequest(BaseModel):
    user_id: str
    theme: str  # "light" or "dark"


class SimulationStageRequest(BaseModel):
    stage: str  # "ticket_1", "ticket_2", "ticket_3"


# -------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Renders the main dashboard page."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "environment": settings.ENVIRONMENT,
            "app_name": settings.APP_NAME,
        },
    )


@app.get("/health")
async def health_check():
    """Health check endpoint required by Render auto-deploy."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/features")
async def get_feature_flags(user_id: Optional[str] = Query("anonymous")):
    """Evaluates and returns feature flag statuses for the requested user."""
    summary = feature_flag_service.get_status_summary(user_id)
    return JSONResponse(content=summary)


@app.post("/api/user/preferences")
async def save_user_preference(payload: UserPreferenceRequest):
    """Ticket 3: Persists user theme preference in the backend."""
    USER_PREFERENCES[payload.user_id] = payload.theme
    return {
        "status": "success",
        "user_id": payload.user_id,
        "theme": payload.theme,
    }


@app.get("/api/user/preferences")
async def get_user_preference(user_id: str = Query("anonymous")):
    """Retrieves persisted user theme preference."""
    theme = USER_PREFERENCES.get(user_id, "light")
    return {
        "user_id": user_id,
        "theme": theme,
    }


@app.post("/api/admin/toggle-simulation")
async def update_simulation_stage(payload: SimulationStageRequest):
    """Allows instructors/students to switch between Ticket 1, Ticket 2, and Ticket 3."""
    success = feature_flag_service.set_simulation_stage(payload.stage)
    if not success:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid stage '{payload.stage}'. Must be ticket_1, ticket_2, or ticket_3"},
        )
    return {
        "status": "success",
        "active_stage": payload.stage,
        "details": feature_flag_service.get_status_summary(),
    }

@app.post("/api/pagos-express")
async def process_pago_express(user_id: str = Query("anonymous")):
    """Simulates Pagos Express with telemetry."""
    is_enabled = feature_flag_service.is_pagos_express_enabled(user_id)
    if not is_enabled:
        return JSONResponse(
            status_code=403, 
            content={"error": "Pagos Express is disabled for this user. Fallback to normal payment."}
        )
    
    # Telemetry simulation (Taller 6 Action 1)
    # Here we would log to Datadog/NewRelic to observe the release
    import random
    if random.random() < 0.1:  # 10% simulated failure
        return JSONResponse(status_code=500, content={"error": "Payment Gateway Error"})
        
    return {"status": "success", "message": "Pago Express processed in 1-click!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
