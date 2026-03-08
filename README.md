# Email Agent (FastAPI + Gmail + OpenAI)

This project is an email workflow assistant that:
- Connects a Gmail inbox via OAuth
- Reads email threads
- Classifies inbound replies with an LLM
- Decides follow-up/reply state for each thread
- Creates Gmail drafts when action is needed
- Serves a dashboard UI to review everything

## What Happens End-to-End

1. You authenticate with Google at `/login`.
2. Google redirects to `/oauth/callback`.
3. The app stores OAuth tokens in SQLite (`users` table).
4. Dashboard (`/dashboard`) loads and calls `/threads/{email}`.
5. `/threads/{email}` runs `process_threads(...)`, which:
   - Pulls all Gmail threads
   - Parses message metadata/body
   - Computes follow-up/reply state
   - Classifies inbound content
   - Creates/reuses drafts
   - Returns normalized thread rows + analytics
6. Dashboard renders those rows and action buttons (Draft/View).

## Project Structure

- `app/main.py`  
  FastAPI entrypoint, OAuth routes, router registration.

- `app/core/database.py`  
  SQLAlchemy engine/session/base setup (`email_agent.db`).

- `app/models/user.py`  
  Stores Gmail OAuth credentials per email.

- `app/models/draft.py`  
  Stores per-thread draft/cache metadata.

- `app/services/gmail_service.py`  
  Gmail API client creation + Gmail draft create/find helpers.

- `app/services/llm_service.py`  
  LLM-based classification and draft text generation.

- `app/services/draft_service.py`  
  Cache utilities for draft existence, state keys, classification cache.

- `app/services/thread_service.py`  
  Main logic pipeline for thread processing and analytics.

- `app/routes/threads.py`  
  API endpoint returning processed thread data.

- `app/routes/dashboard.py`  
  HTML/JS dashboard UI.

## Thread Processing Logic (Exactly What It Does)

`process_threads(service, my_email)` in `thread_service.py`:

1. Fetches all threads from Gmail.
2. Removes Gmail messages with label `DRAFT` from analysis.
3. Identifies:
   - First/last message
   - Outbound timestamps
   - Inbound timestamps
   - Contact email and direction (`outbound` vs `inbound`)
4. Detects whether a thread has an inbound reply (`reply_detected`).
5. Counts follow-ups sent (only outbound messages sent before first inbound reply).
6. Computes:
   - `days_since_first_email`
   - `days_since_last_email`
   - `reply_time_days` (for analytics)
7. Classifies inbound content:
   - Uses cached category if `message_count` unchanged
   - Else runs `llm_classify(...)`
   - Categories: `positive`, `negative`, `requesting_more_info`, `out_of_office`, `wrong_person`, `unsubscribe`
8. Applies follow-up timing rules for outbound no-reply threads:
   - Follow-up 1 due at day 3
   - Follow-up 2 due at day 7
   - Follow-up 3 due at day 14
9. Handles draft lifecycle:
   - Checks if cached draft still exists in Gmail (`get_existing_draft`)
   - If still present, reuses it (shows Draft button)
   - If missing/sent/deleted, clears cached `draft_id`
   - Generates new draft only when state key changed and no active draft
10. Prevents duplicate reply drafts after you already responded:
    - Uses `has_our_reply` (latest outbound is after latest inbound)
    - Reply drafts are generated only when `not has_our_reply`
11. Assigns `lead_state` and `status_message` for UI.
12. Builds analytics:
    - `total_outbound`
    - `total_replied`
    - `reply_rate_pct`
    - `avg_reply_time_days`
    - `category_breakdown`

## Draft State Model

`drafts` table tracks:
- `thread_id`: primary key
- `draft_id`: active unsent Gmail draft ID
- `draft_generated_for`: state key (example: `followup_2`, `reply_positive_5`)
- `reply_category`, `message_count`: classification cache

State keys prevent regenerating identical drafts on each refresh.

## API Endpoints

- `GET /`  
  Health message.

- `GET /login`  
  Starts Gmail OAuth.

- `GET /oauth/callback`  
  Finishes OAuth and stores tokens.

- `GET /dashboard`  
  Serves dashboard UI.

- `GET /threads/{email}`  
  Returns `{ "threads": [...], "analytics": {...} }`.

## Local Setup

1. Create a virtual environment and install dependencies:
   - `python -m venv venv`
   - `venv\Scripts\activate` (Windows PowerShell)
   - `python -m pip install -r requirements.txt`
2. Create Google OAuth credentials (Web application) in Google Cloud Console:
   - Enable Gmail API for your Google Cloud project
   - Create OAuth Client ID of type `Web application`
   - Add Authorized redirect URI exactly: `http://localhost:8000/oauth/callback`
   - Download the OAuth client JSON
3. Create local secrets files (do not commit these):
   - Put downloaded Google OAuth JSON at project root as `credentials.json`
   - Copy `.env.example` -> `.env`
4. Set your OpenAI API key:
   - PowerShell (recommended): `$env:OPENAI_API_KEY="your_openai_key"`
   - Or set it as a system/user environment variable before running the app
5. Start server:
   - `uvicorn app.main:app --reload`
6. Authenticate Gmail:
   - Open `http://localhost:8000/login`
   - Complete consent screen in browser
7. Open dashboard:
   - `http://localhost:8000/dashboard`
8. Dashboard mailbox resolution:
   - The dashboard now auto-detects mailbox email from:
     1) `?email=...` URL param
     2) last saved value in browser localStorage
     3) backend endpoint `/threads/default-email` (most recently authenticated user)
   - To force a specific mailbox, open:
     - `http://localhost:8000/dashboard?email=your@gmail.com`

## Notes

- OAuth is configured for local HTTP via `OAUTHLIB_INSECURE_TRANSPORT=1` in `app/main.py`.
- `.gitignore` already excludes secrets and local data (`credentials.json`, `.env`, `*.db`).
- `app/services/thread_state.json` exists but is not used by the current pipeline.
