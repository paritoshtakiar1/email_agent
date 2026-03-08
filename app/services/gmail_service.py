"""Helpers for Gmail API authentication and draft operations."""

import base64
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.database import SessionLocal
from app.models.user import User


def get_gmail_service(email: str):
    """Build an authenticated Gmail API client for a previously authorized user.

    Args:
        email: Gmail address used as the key in the local users table.

    Returns:
        A Google API Gmail service object.

    Raises:
        Exception: If no OAuth credentials are stored for the given email.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
    finally:
        db.close()

    if not user:
        raise Exception("User not authenticated")

    creds = Credentials(
        token=user.access_token,
        refresh_token=user.refresh_token,
        token_uri=user.token_uri,
        client_id=user.client_id,
        client_secret=user.client_secret,
        scopes=user.scopes.split(","),
    )
    return build("gmail", "v1", credentials=creds)


def create_gmail_draft(service, to_email, subject, body, thread_id=None, message_id=None):
    """Create a Gmail draft, optionally attached to an existing thread/reply chain.

    Args:
        service: Authenticated Gmail API service object.
        to_email: Recipient email address.
        subject: Email subject line.
        body: Plain-text email body.
        thread_id: Gmail thread ID for in-thread draft creation.
        message_id: Original message ID used for In-Reply-To/References headers.

    Returns:
        Gmail draft ID string if created, otherwise None when body is empty.
    """
    if not body:
        return None

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject

    # Preserve email threading in recipients' inboxes.
    if message_id:
        message["In-Reply-To"] = message_id
        message["References"] = message_id

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {"message": {"raw": raw}}

    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    draft = service.users().drafts().create(userId="me", body=draft_body).execute()
    return draft["id"]


def get_gmail_draft(service, thread_id):
    """Find and return a draft ID that belongs to the given Gmail thread.

    Args:
        service: Authenticated Gmail API service object.
        thread_id: Gmail thread ID to search for.

    Returns:
        Draft ID string if found, otherwise None.
    """
    results = service.users().drafts().list(userId="me").execute()
    drafts = results.get("drafts", [])

    for draft in drafts:
        draft_data = service.users().drafts().get(
            userId="me",
            id=draft["id"],
        ).execute()
        message = draft_data.get("message", {})
        if message.get("threadId") == thread_id:
            return draft["id"]

    return None
