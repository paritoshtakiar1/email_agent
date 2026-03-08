# app/routes/threads.py

from fastapi import APIRouter

from app.core.database import SessionLocal
from app.models.user import User
from app.services.gmail_service import get_gmail_service
from app.services.thread_service import process_threads

router = APIRouter()


@router.get("/threads/default-email")
def get_default_email():
    """Return the most recently authenticated mailbox email, if available."""
    db = SessionLocal()
    try:
        user = db.query(User).order_by(User.id.desc()).first()
        return {"email": user.email if user else None}
    finally:
        db.close()


@router.get("/threads/{email}")
def get_threads(email: str):
    """Return processed thread data + analytics for a specific authenticated mailbox."""
    service = get_gmail_service(email)
    return process_threads(service, email)
