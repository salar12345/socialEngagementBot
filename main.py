from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from db import init_db
from crud import create_or_update_profile, get_profile, latest_count, counts_24h_delta, top_changes_last_24h
from schemas import ProfileCreate, ProfileRead, AlertSettings, Insight
from tasks import startup, shutdown
from social_fetcher import mock_fetcher
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Social Network Engagement Bot")
security = HTTPBasic()

API_USER = os.getenv("API_USER", "admin")
API_PASS = os.getenv("API_PASS", "password")


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != API_USER or credentials.password != API_PASS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid auth",
                            headers={"WWW-Authenticate": "Basic"})
    return credentials.username


@app.on_event("startup")
async def on_startup():
    init_db()
    await startup(app)


@app.on_event("shutdown")
async def on_shutdown():
    await shutdown(app)


@app.post("/profiles", response_model=ProfileRead)
async def add_profile(payload: ProfileCreate, user: str = Depends(check_auth)):
    p = create_or_update_profile(payload.handle, payload.platform, payload.alert_threshold, payload.telegram_chat_id)
    mock_fetcher.register(payload.handle)
    return ProfileRead(id=p.id, handle=p.handle, platform=p.platform, alert_threshold=p.alert_threshold,
                       telegram_chat_id=p.telegram_chat_id)


@app.get("/profiles/{handle}", response_model=ProfileRead)
async def get_profile_endpoint(handle: str, user: str = Depends(check_auth)):
    p = get_profile(handle)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileRead(id=p.id, handle=p.handle, platform=p.platform, alert_threshold=p.alert_threshold,
                       telegram_chat_id=p.telegram_chat_id)


@app.put("/profiles/{handle}/alerts", response_model=AlertSettings)
async def set_alerts(handle: str, settings: AlertSettings, user: str = Depends(check_auth)):
    p = get_profile(handle)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    p = create_or_update_profile(handle, p.platform, settings.alert_threshold, settings.telegram_chat_id)
    return AlertSettings(alert_threshold=p.alert_threshold, telegram_chat_id=p.telegram_chat_id)


@app.get("/profiles/{handle}/insight", response_model=Insight)
async def get_insight(handle: str, user: str = Depends(check_auth)):
    p = get_profile(handle)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    latest = latest_count(p.id)
    latest_val = latest.count if latest else 0
    delta = counts_24h_delta(p.id)
    return Insight(handle=p.handle, latest_count=latest_val, delta_24h=delta)


@app.get("/insights/top_changes")
async def get_top_changes(user: str = Depends(check_auth)):
    results = top_changes_last_24h()
    return {"top_changes": results}
