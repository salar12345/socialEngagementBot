import asyncio
import os
from dotenv import load_dotenv
from db import init_db, get_session
from models import Profile, AlertLog
from social_fetcher import mock_fetcher
from crud import insert_history, log_alert
from telegram_notifier import send_telegram_message
from sqlmodel import select

load_dotenv()

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))


async def monitor_loop(app):
    print("Starting monitor loop with interval", POLL_INTERVAL)
    init_db()
    while True:
        with get_session() as session:
            profiles = session.exec(select(Profile)).all()
        for p in profiles:
            if not p.monitor:
                continue
            mock_fetcher.register(p.handle)
            count = mock_fetcher.fetch(p.handle)
            insert_history(p.id, count)
            if p.alert_threshold is not None:
                existing = None
                with get_session() as session:
                    existing = session.exec(
                        select(AlertLog).where(AlertLog.profile_id == p.id, AlertLog.threshold == p.alert_threshold)
                    ).one_or_none()
                if count >= p.alert_threshold and existing is None:
                    text = f"🎉 Profile @{p.handle} reached {count} followers (threshold: {p.alert_threshold})"
                    chat = p.telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID")
                    await send_telegram_message(chat, text)
                    log_alert(p.id, p.alert_threshold, text)
        await asyncio.sleep(POLL_INTERVAL)


async def startup(app):
    task = asyncio.create_task(monitor_loop(app))
    app.state.monitor_task = task


async def shutdown(app):
    if hasattr(app.state, "monitor_task"):
        app.state.monitor_task.cancel()
        try:
            await app.state.monitor_task
        except asyncio.CancelledError:
            pass
