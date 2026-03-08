"""Persistence helpers for per-thread draft and classification cache records."""

from app.core.database import SessionLocal
from app.models.draft import Draft


def get_existing_draft(service, thread_id):
    """Return a valid unsent Gmail draft ID for a thread if it still exists.

    This method keeps the local DB cache in sync with Gmail:
    - If a cached draft exists in Gmail, it returns that draft ID.
    - If Gmail no longer has the draft (sent/deleted), local draft fields are reset.

    Args:
        service: Authenticated Gmail API service object.
        thread_id: Gmail thread ID.

    Returns:
        Gmail draft ID string if an unsent draft exists, otherwise None.
    """
    db = SessionLocal()
    try:
        record = db.query(Draft).filter(Draft.thread_id == thread_id).first()
        if not record or not record.draft_id:
            return None

        try:
            service.users().drafts().get(userId="me", id=record.draft_id).execute()
            return record.draft_id
        except Exception:
            # Draft was sent/deleted: clear local draft state so future generation can run.
            record.draft_id = None
            record.draft_generated_for = None
            db.commit()
            return None
    finally:
        db.close()


def save_draft(thread_id, draft_id, generated_for=None):
    """Create or update a thread's cached draft record.

    Args:
        thread_id: Gmail thread ID.
        draft_id: Gmail draft ID.
        generated_for: Optional state key representing why this draft was generated.
    """
    db = SessionLocal()
    try:
        existing = db.query(Draft).filter(Draft.thread_id == thread_id).first()
        if existing:
            existing.draft_id = draft_id
            if generated_for:
                existing.draft_generated_for = generated_for
        else:
            db.add(
                Draft(
                    thread_id=thread_id,
                    draft_id=draft_id,
                    draft_generated_for=generated_for,
                )
            )
        db.commit()
    finally:
        db.close()


def get_cached_category(thread_id):
    """Fetch cached reply category and message count for a thread.

    Args:
        thread_id: Gmail thread ID.

    Returns:
        Tuple of (reply_category, message_count). Returns (None, None) if absent.
    """
    db = SessionLocal()
    try:
        record = db.query(Draft).filter(Draft.thread_id == thread_id).first()
        if record and record.reply_category:
            return record.reply_category, record.message_count
        return None, None
    finally:
        db.close()


def save_category(thread_id, category, message_count):
    """Store or update the thread's LLM classification cache."""
    db = SessionLocal()
    try:
        existing = db.query(Draft).filter(Draft.thread_id == thread_id).first()
        if existing:
            existing.reply_category = category
            existing.message_count = message_count
        else:
            db.add(
                Draft(
                    thread_id=thread_id,
                    reply_category=category,
                    message_count=message_count,
                )
            )
        db.commit()
    finally:
        db.close()


def should_generate_draft(thread_id, current_state):
    """Decide if a new draft should be generated for the current thread state.

    Rules:
    - No cache record -> generate.
    - Existing unsent draft_id -> do not generate.
    - No unsent draft and state key changed -> generate.

    Args:
        thread_id: Gmail thread ID.
        current_state: Deterministic state key (for example: ``followup_2``).

    Returns:
        True when generation should run, False otherwise.
    """
    db = SessionLocal()
    try:
        record = db.query(Draft).filter(Draft.thread_id == thread_id).first()
        if not record:
            return True
        if record.draft_id:
            return False
        return record.draft_generated_for != current_state
    finally:
        db.close()
