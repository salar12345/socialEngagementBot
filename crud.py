from sqlmodel import select
from db import get_session
from models import Profile, FollowerHistory, AlertLog
from datetime import datetime, timedelta


def create_or_update_profile(handle: str, platform: str = "mock", alert_threshold: int = None,
                             telegram_chat_id: str = None):
    with get_session() as session:
        stmt = select(Profile).where(Profile.handle == handle, Profile.platform == platform)
        res = session.exec(stmt).one_or_none()
        if res:
            res.alert_threshold = alert_threshold
            res.telegram_chat_id = telegram_chat_id
            session.add(res)
            session.commit()
            session.refresh(res)
            return res
        p = Profile(handle=handle, platform=platform, alert_threshold=alert_threshold,
                    telegram_chat_id=telegram_chat_id)
        session.add(p)
        session.commit()
        session.refresh(p)
        return p


def get_profile(handle: str, platform: str = "mock"):
    with get_session() as session:
        stmt = select(Profile).where(Profile.handle == handle, Profile.platform == platform)
        return session.exec(stmt).one_or_none()


def insert_history(profile_id: int, count: int):
    with get_session() as session:
        h = FollowerHistory(profile_id=profile_id, count=count)
        session.add(h)
        session.commit()
        session.refresh(h)
        return h


def log_alert(profile_id: int, threshold: int, message: str):
    with get_session() as session:
        a = AlertLog(profile_id=profile_id, threshold=threshold, message=message)
        session.add(a)
        session.commit()
        session.refresh(a)
        return a


def latest_count(profile_id: int):
    with get_session() as session:
        stmt = select(FollowerHistory).where(FollowerHistory.profile_id == profile_id).order_by(
            FollowerHistory.ts.desc()).limit(1)
        return session.exec(stmt).one_or_none()


def counts_24h_delta(profile_id: int):
    with get_session() as session:
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)
        stmt_recent = select(FollowerHistory).where(FollowerHistory.profile_id == profile_id).order_by(
            FollowerHistory.ts.desc())
        all_hist = session.exec(stmt_recent).all()
        if not all_hist:
            return None
        latest = all_hist[0].count
        older = None
        for h in reversed(all_hist):
            if h.ts <= day_ago:
                older = h
                break
        if older is None:
            older = all_hist[-1]
        return latest - older.count


def top_changes_last_24h(limit: int = 5):
    with get_session() as session:
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)
        profiles = session.exec(select(Profile)).all()
        results = []
        for p in profiles:
            stmt = select(FollowerHistory).where(FollowerHistory.profile_id == p.id,
                                                 FollowerHistory.ts >= day_ago).order_by(FollowerHistory.ts)
            hist = session.exec(stmt).all()
            if not hist:
                continue
            first = hist[0].count
            last = hist[-1].count
            results.append({"handle": p.handle, "delta": last - first})
        results.sort(key=lambda x: abs(x["delta"]), reverse=True)
        return results[:limit]
