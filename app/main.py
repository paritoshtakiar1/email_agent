"""FastAPI entrypoint for Gmail auth, dashboard, and thread-processing APIs."""

import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.core.database import Base, SessionLocal, engine
from app.models.draft import Draft
from app.models.user import User

# Local development only: allows OAuth callback over plain HTTP.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Ensure all declared SQLAlchemy models have backing tables.
Base.metadata.create_all(bind=engine)

app = FastAPI()

CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
REDIRECT_URI = "http://localhost:8000/oauth/callback"

# In-memory store for OAuth flow state between /login and /oauth/callback.
oauth_flow_store = {}


@app.get("/")
def home():
    """Health endpoint used to confirm the backend is running."""
    return {"message": "Email Agent Backend Running"}


@app.get("/login")
def login():
    """Start Google OAuth and redirect the user to Google's consent screen."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    # Persist the full flow so callback can exchange code for tokens.
    oauth_flow_store["flow"] = flow
    return RedirectResponse(authorization_url)


@app.get("/oauth/callback")
def oauth_callback(request: Request):
    """Finalize OAuth, then store Gmail credentials for the authenticated user."""
    flow = oauth_flow_store.get("flow")
    if not flow:
        return {"error": "OAuth flow not found. Restart login."}

    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    db = SessionLocal()
    try:
        # Build Gmail service to fetch the mailbox identity behind these tokens.
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        email = profile["emailAddress"]

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email)

        # Persist OAuth token material for later API calls.
        user.access_token = credentials.token
        user.refresh_token = credentials.refresh_token
        user.token_uri = credentials.token_uri
        user.client_id = credentials.client_id
        user.client_secret = credentials.client_secret
        user.scopes = ",".join(credentials.scopes)

        db.add(user)
        db.commit()
    finally:
        db.close()

    return {"message": "Authentication successful", "email": email}


from app.routes import dashboard, threads

app.include_router(dashboard.router)
app.include_router(threads.router)
