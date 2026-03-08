"""Core orchestration for turning raw Gmail threads into dashboard-ready records."""

from datetime import datetime
from email.utils import parsedate_to_datetime
from app.services.gmail_service import create_gmail_draft

import base64
from app.services.llm_service import llm_classify, generate_followup, generate_reply

from app.services.draft_service import (
    get_existing_draft, save_draft,
    get_cached_category, save_category, should_generate_draft
)

import re


def clean_email(address):
    """Extract plain email from headers like ``Name <user@example.com>``."""
    match = re.search(r"<(.+?)>", address)
    if match:
        return match.group(1)
    return address


def extract_message_id(message):
    """Return RFC Message-ID header for a Gmail message payload."""
    headers = message["payload"]["headers"]
    for header in headers:
        if header["name"] == "Message-ID":
            return header["value"]
    return None


def extract_sender(message):
    """Return ``From`` header value, defaulting to ``Unknown``."""
    headers = message["payload"]["headers"]
    for header in headers:
        if header["name"] == "From":
            return header["value"]
    return "Unknown"


def extract_recipient(message):
    """Return ``To`` header value, defaulting to ``Unknown``."""
    headers = message["payload"]["headers"]
    for header in headers:
        if header["name"] == "To":
            return header["value"]
    return "Unknown"


def extract_subject(message):
    """Return ``Subject`` header value, defaulting to ``No Subject``."""
    headers = message["payload"]["headers"]
    for header in headers:
        if header["name"] == "Subject":
            return header["value"]
    return "No Subject"


def extract_body(message):
    """Decode plain-text body from Gmail payload (single-part or multipart)."""
    payload = message["payload"]

    if "data" in payload.get("body", {}):
        data = payload["body"]["data"]
        decoded = base64.urlsafe_b64decode(data)
        return decoded.decode("utf-8", errors="ignore")

    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    decoded = base64.urlsafe_b64decode(data)
                    return decoded.decode("utf-8", errors="ignore")

    return ""


def is_lead_relevant(sender):
    """Heuristic filter to ignore automated/newsletter senders."""
    sender_lower = sender.lower()
    blocked_keywords = [
        "noreply", "no-reply", "newsletter", "notification",
        "community", "support", "updates", "mailer-daemon",
        "postmaster", "donotreply"
    ]
    for word in blocked_keywords:
        if word in sender_lower:
            return False
    return True


def detect_meeting_intent(text):
    """Detect scheduling intent keywords in a reply."""
    if not text:
        return False
    text_lower = text.lower()
    meeting_phrases = [
        "schedule a call", "schedule a meeting", "set up a call",
        "set up a meeting", "book a time", "book a call",
        "let's meet", "let's hop on a call", "can we meet",
        "can we talk", "next week", "this week",
        "available for a call", "free for a chat", "free this week",
        "free next week", "15 minutes", "30 minutes",
        "zoom", "google meet", "calendly", "cal.com",
        "what time works", "when works for you",
        "tuesday", "wednesday", "thursday", "friday",
        "2pm", "3pm", "10am", "11am",
    ]
    for phrase in meeting_phrases:
        if phrase in text_lower:
            return True
    return False


def _create_draft_and_save(service, contact_email, subject, body,
                           thread_id, message_id, my_email, state_key):
    """Create Gmail draft + persist cache metadata, then return dashboard link."""
    draft_id = create_gmail_draft(
        service, contact_email, subject, body, thread_id, message_id
    )
    if draft_id:
        save_draft(thread_id, draft_id, generated_for=state_key)
        return f"https://mail.google.com/mail/u/?authuser={my_email}#inbox/{thread_id}"
    return None


def process_threads(service, my_email):
    """Build dashboard data by analyzing Gmail threads and generating drafts.

    The function performs these stages per thread:
    1) Parse senders, timestamps, bodies, and reply direction.
    2) Classify inbound messages and compute follow-up status.
    3) Reuse/create drafts when action is needed.
    4) Emit normalized thread objects plus aggregate analytics.

    Args:
        service: Authenticated Gmail API service object.
        my_email: Current mailbox email used to determine message ownership.

    Returns:
        Dict with ``threads`` list and ``analytics`` summary.
    """
    threads = []
    request = service.users().threads().list(userId="me")

    while request is not None:
        response = request.execute()
        threads.extend(response.get("threads", []))
        request = service.users().threads().list_next(request, response)

    processed = []

    for thread in threads:
        thread_data = service.users().threads().get(
            userId="me",
            id=thread["id"]
        ).execute()

        messages = [
            msg for msg in thread_data["messages"]
            if "DRAFT" not in msg.get("labelIds", [])
        ]

        if not messages:
            continue

        first_msg = messages[0]
        last_msg = messages[-1]
        message_count = len(messages)

        subject = extract_subject(first_msg)
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        # ── Timestamps + outbound tracking ──
        first_outbound_timestamp = None
        last_outbound_timestamp = None
        outbound_count = 0
        first_outbound_message_id = None

        for msg in messages:
            sender = extract_sender(msg)
            if my_email in sender and "SENT" in msg.get("labelIds", []):
                headers = msg["payload"]["headers"]
                for header in headers:
                    if header["name"] == "Date":
                        ts = parsedate_to_datetime(header["value"])
                        if first_outbound_timestamp is None:
                            first_outbound_timestamp = ts
                            first_outbound_message_id = extract_message_id(msg)
                        last_outbound_timestamp = ts
                        break
                outbound_count += 1

        # ── Senders ──
        first_sender = extract_sender(first_msg)
        last_sender = extract_sender(last_msg)

        # ── Thread type ──
        thread_type = "outbound" if my_email in first_sender else "inbound"

        # ══════════════════════════════════════
        #  REPLY DETECTION + INBOUND MESSAGE TRACKING
        #  For outbound: any inbound msg = they replied
        #  For inbound: track their messages for classification + drafting
        # ══════════════════════════════════════
        has_inbound_reply = False
        last_inbound_body = ""
        last_inbound_msg = None
        first_inbound_timestamp = None
        last_inbound_timestamp = None
        has_our_reply = False

        for msg in messages:
            sender = extract_sender(msg)
            if my_email not in sender:
                # Message from someone else
                last_inbound_body = extract_body(msg)
                last_inbound_msg = msg
                if thread_type == "outbound":
                    has_inbound_reply = True
                msg_inbound_timestamp = None
                for h in msg["payload"]["headers"]:
                    if h["name"] == "Date":
                        msg_inbound_timestamp = parsedate_to_datetime(h["value"])
                        break
                if msg_inbound_timestamp:
                    if first_inbound_timestamp is None:
                        first_inbound_timestamp = msg_inbound_timestamp
                    last_inbound_timestamp = msg_inbound_timestamp

        # True only when we've already sent a message after their latest inbound.
        has_our_reply = (
            last_inbound_timestamp is not None
            and last_outbound_timestamp is not None
            and last_outbound_timestamp > last_inbound_timestamp
        )

        # For outbound threads: reply_detected = they replied
        # For inbound threads: reply_detected stays False (they initiated, not replied)
        reply_detected = has_inbound_reply

        # ══════════════════════════════════════
        #  FOLLOW-UP COUNT — only count outbound
        #  messages sent BEFORE any inbound reply
        # ══════════════════════════════════════
        followup_outbound_count = 0
        saw_first_outbound = False

        for msg in messages:
            sender = extract_sender(msg)
            if my_email in sender and "SENT" in msg.get("labelIds", []):
                if not saw_first_outbound:
                    saw_first_outbound = True
                    continue  # skip original email

                # Get this message's timestamp
                msg_date = None
                for h in msg["payload"]["headers"]:
                    if h["name"] == "Date":
                        msg_date = parsedate_to_datetime(h["value"])
                        break

                # Only count as follow-up if sent BEFORE any inbound reply
                if msg_date and first_inbound_timestamp and msg_date > first_inbound_timestamp:
                    continue  # this is a reply-back, not a follow-up
                followup_outbound_count += 1

        followups_sent = followup_outbound_count

        # ── Days calculations ──
        days_since_first_email = None
        days_since_last_email = None
        last_email_date = None

        now = datetime.now(tz=first_outbound_timestamp.tzinfo) if first_outbound_timestamp else None

        if first_outbound_timestamp:
            days_since_first_email = (now - first_outbound_timestamp).days

        if last_outbound_timestamp:
            days_since_last_email = (now - last_outbound_timestamp).days
            last_email_date = last_outbound_timestamp.strftime("%Y-%m-%d")

        # ── Contact info ──
        if my_email in first_sender:
            contact_email = clean_email(extract_recipient(first_msg))
            contact_type = "outbound"
        else:
            contact_email = clean_email(first_sender)
            contact_type = "inbound"

        first_body = extract_body(first_msg)
        last_body = extract_body(last_msg)

        # ── Reply time for analytics ──
        reply_time_days = None
        if reply_detected and first_outbound_timestamp and first_inbound_timestamp:
            reply_time_days = (first_inbound_timestamp - first_outbound_timestamp).days

        # ══════════════════════════════════════
        #  CLASSIFICATION (cached by message count)
        #  - Outbound + reply: classify their inbound reply
        #  - Inbound thread: classify their message
        #  - Outbound + no reply: "Waiting for reply"
        # ══════════════════════════════════════
        classify_body = None

        if reply_detected and last_inbound_body:
            # Outbound thread, they replied — classify their reply
            classify_body = last_inbound_body.split("On ")[0]
        elif thread_type == "inbound" and last_inbound_body:
            # Inbound thread — classify their message
            classify_body = last_inbound_body.split("On ")[0]

        if classify_body and classify_body.strip():
            cached_cat, cached_count = get_cached_category(thread["id"])
            if cached_cat and cached_count == message_count:
                reply_category = cached_cat
            else:
                reply_category = llm_classify(classify_body)
                save_category(thread["id"], reply_category, message_count)
        elif reply_detected:
            cached_cat, _ = get_cached_category(thread["id"])
            reply_category = cached_cat if cached_cat else "neutral"
        else:
            reply_category = "Waiting for reply"

        # ── Lead relevance ──
        lead_relevant = is_lead_relevant(first_sender)

        # ── Meeting intent ──
        meeting_intent = False
        if reply_detected:
            meeting_intent = detect_meeting_intent(last_inbound_body or last_body)

        # ══════════════════════════════════════
        #  FOLLOW-UP SEQUENCING
        #  STOPS when reply_detected = True
        # ══════════════════════════════════════
        followup_stage = followups_sent
        followup_due = False
        draft_needed = False
        days_until_followup = None
        next_followup = followups_sent + 1

        if (thread_type == "outbound"
            and not reply_detected
            and reply_category not in ["unsubscribe", "negative"]):

            if days_since_first_email is not None:

                if days_since_first_email >= 14:
                    expected_stage = 3
                elif days_since_first_email >= 7:
                    expected_stage = 2
                elif days_since_first_email >= 3:
                    expected_stage = 1
                else:
                    expected_stage = 0

                next_followup = followups_sent + 1

                if next_followup <= 3 and next_followup <= expected_stage:
                    followup_stage = next_followup
                    followup_due = True
                    draft_needed = True

                    if next_followup == 1:
                        days_until_followup = 3 - days_since_first_email
                    elif next_followup == 2:
                        days_until_followup = 7 - days_since_first_email
                    elif next_followup == 3:
                        days_until_followup = 14 - days_since_first_email

                elif next_followup <= 3:
                    followup_stage = followups_sent
                    followup_due = False

                    if next_followup == 1:
                        days_until_followup = 3 - days_since_first_email
                    elif next_followup == 2:
                        days_until_followup = 7 - days_since_first_email
                    elif next_followup == 3:
                        days_until_followup = 14 - days_since_first_email

                    if days_until_followup is not None and days_until_followup <= 1:
                        draft_needed = True

                else:
                    followup_stage = 3
                    followup_due = False
                    days_until_followup = None

        # ══════════════════════════════════════
        #  DRAFT GENERATION
        #
        #  How it works:
        #  1. get_existing_draft checks Gmail — if draft was
        #     sent/deleted, clears draft_id AND draft_generated_for
        #  2. should_generate_draft checks if current state_key
        #     differs from what we last generated for
        #  3. State key changes when: reply comes in, new follow-up
        #     stage, message count changes
        # ══════════════════════════════════════
        draft_followup = None
        draft_link = None

        # Check if unsent draft still exists in Gmail
        existing_draft_id = get_existing_draft(service, thread["id"])

        if existing_draft_id:
            # Unsent draft exists — just link to it
            draft_link = f"https://mail.google.com/mail/u/?authuser={my_email}#inbox/{thread['id']}"

        else:
            # No unsent draft — determine if we need to create one

            # Build state key based on what kind of draft this would be
            if draft_needed and not reply_detected:
                state_key = f"followup_{next_followup}"
            elif (reply_detected
                  and not has_our_reply
                  and reply_category in ["positive", "requesting_more_info", "negative", "wrong_person"]):
                state_key = f"reply_{reply_category}_{message_count}"
            elif thread_type == "inbound" and not has_our_reply and reply_category in ["positive", "requesting_more_info", "negative", "wrong_person"]:
                # Inbound email we haven't replied to yet
                state_key = f"inbound_{reply_category}_{message_count}"
            else:
                state_key = None

            if state_key and should_generate_draft(thread["id"], state_key):

                last_msg_id = extract_message_id(last_msg)
                reply_msg_id = extract_message_id(last_inbound_msg) if last_inbound_msg else last_msg_id

                if draft_needed and not reply_detected:
                    # Follow-up for unreplied outbound thread
                    draft_stage = next_followup if next_followup <= 3 else followup_stage
                    print(f"  [GEN] {thread['id'][:8]}: Generating follow-up {draft_stage}")
                    draft_followup = generate_followup(first_body, draft_stage)
                    if draft_followup:
                        draft_link = _create_draft_and_save(
                            service, contact_email, subject, draft_followup,
                            thread["id"], first_outbound_message_id, my_email, state_key
                        )
                        print(f"  [GEN] {thread['id'][:8]}: Follow-up draft created!")

                elif (reply_detected
                      and not has_our_reply
                      and reply_category in ["positive", "requesting_more_info", "negative", "wrong_person"]):
                    # Outbound thread got a reply — auto-reply based on category
                    reply_body = last_inbound_body if last_inbound_body else last_body
                    print(f"  [GEN] {thread['id'][:8]}: Generating {reply_category} reply (outbound replied)")
                    draft_followup = generate_reply(first_body, reply_body, reply_category)
                    if draft_followup:
                        draft_link = _create_draft_and_save(
                            service, contact_email, subject, draft_followup,
                            thread["id"], reply_msg_id, my_email, state_key
                        )
                        print(f"  [GEN] {thread['id'][:8]}: Reply draft created!")
                    else:
                        print(f"  [GEN] {thread['id'][:8]}: generate_reply returned None!")

                elif thread_type == "inbound" and not has_our_reply and reply_category in ["positive", "requesting_more_info", "negative", "wrong_person"]:
                    # Inbound email — someone reached out to us, draft a response
                    inbound_body = last_inbound_body if last_inbound_body else last_body
                    print(f"  [GEN] {thread['id'][:8]}: Generating {reply_category} reply (inbound, no reply yet)")
                    draft_followup = generate_reply("", inbound_body, reply_category)
                    if draft_followup:
                        draft_link = _create_draft_and_save(
                            service, contact_email, subject, draft_followup,
                            thread["id"], reply_msg_id, my_email, state_key
                        )
                        print(f"  [GEN] {thread['id'][:8]}: Inbound reply draft created!")
                    else:
                        print(f"  [GEN] {thread['id'][:8]}: generate_reply returned None!")

                # out_of_office and unsubscribe: NO auto-reply

        # ══════════════════════════════════════
        #  LEAD STATE
        # ══════════════════════════════════════
        lead_state = "cold"
        action_required = False

        # For outbound threads: lead state based on their reply
        # For inbound threads: lead state based on their initial message
        needs_action = (
            lead_relevant
            and (reply_detected or thread_type == "inbound")
            and reply_category not in ["Waiting for reply", "unsubscribe"]
        )

        if needs_action:
            action_required = True

            if reply_category in ["positive", "requesting_more_info"]:
                lead_state = "warm"
            elif reply_category == "negative":
                lead_state = "closed"
                action_required = False
            elif reply_category == "out_of_office":
                lead_state = "paused"
                action_required = False
            elif reply_category == "wrong_person":
                lead_state = "reroute"
            elif reply_category == "unsubscribe":
                lead_state = "closed"
                action_required = False
            else:
                lead_state = "neutral"

        # ══════════════════════════════════════
        #  STATUS MESSAGE
        # ══════════════════════════════════════
        status_message = ""

        if reply_detected:
            status_map = {
                "positive": "Replied positive." + (" Draft reply ready." if draft_link else ""),
                "requesting_more_info": "Requested info." + (" Draft reply ready." if draft_link else ""),
                "negative": "Declined." + (" Graceful close drafted." if draft_link else ""),
                "wrong_person": "Wrong person." + (" Redirect drafted." if draft_link else ""),
                "out_of_office": "Out of office. Sequence paused.",
                "unsubscribe": "Unsubscribe requested.",
            }
            status_message = status_map.get(reply_category, "Replied.")

        elif thread_type == "inbound":
            # Someone emailed us
            inbound_map = {
                "positive": "Inbound interest." + (" Draft reply ready." if draft_link else ""),
                "requesting_more_info": "Inbound inquiry." + (" Draft reply ready." if draft_link else ""),
                "negative": "Inbound decline.",
                "wrong_person": "Inbound misdirected." + (" Redirect drafted." if draft_link else ""),
                "out_of_office": "Inbound OOO.",
                "unsubscribe": "Unsubscribe.",
            }
            status_message = inbound_map.get(reply_category, "New inbound email.")

        elif thread_type == "outbound":
            if followup_due:
                if days_until_followup is not None and days_until_followup < 0:
                    status_message = f"Follow-up {followup_stage} overdue by {abs(days_until_followup)} days."
                else:
                    status_message = f"Follow-up {followup_stage} ready to send."
            elif days_until_followup is not None:
                if days_until_followup <= 0:
                    status_message = f"Send follow-up {followup_stage + 1} today."
                elif days_until_followup == 1:
                    status_message = f"Follow-up {followup_stage + 1} due tomorrow. Draft ready."
                else:
                    status_message = f"Waiting for reply. Follow-up {followup_stage + 1} in {days_until_followup} days."
            elif followup_stage >= 3:
                status_message = "All follow-ups sent. Waiting for reply."

        # Action items
        action_items = []
        if meeting_intent:
            action_items.append("Schedule meeting — reply contains scheduling intent")

        processed.append({
            "thread_id": thread["id"],
            "contact_email": contact_email,
            "contact_type": contact_type,
            "type": thread_type,
            "lead_relevant": lead_relevant,
            "reply_detected": reply_detected,
            "action_required": action_required,
            "lead_state": lead_state,
            "reply_category": reply_category,
            "days_since_first_email": days_since_first_email,
            "days_since_last_email": days_since_last_email,
            "followup_stage": followup_stage,
            "followups_sent": followups_sent,
            "followup_due": followup_due,
            "draft_followup": draft_followup,
            "last_message_preview": last_body[:120],
            "status_message": status_message,
            "draft_link": draft_link,
            "last_email_date": last_email_date,
            "subject": extract_subject(first_msg),
            "meeting_intent": meeting_intent,
            "action_items": action_items,
            "reply_time_days": reply_time_days,
        })
        print(f"\n=== Thread {thread['id'][:8]} | contact={contact_email} ===")
        print(f"  thread_type={thread_type} | reply_detected={reply_detected}")
        print(f"  reply_category={reply_category} | message_count={message_count}")
        print(f"  draft_needed={draft_needed} | followup_stage={followup_stage}")
        print(f"  has_our_reply={has_our_reply}")
        print(f"  last_inbound_body={last_inbound_body[:50] if last_inbound_body else 'EMPTY'}")
        print(f"  last_inbound_msg={'EXISTS' if last_inbound_msg else 'NONE'}")
    # ══════════════════════════════════════
    #  ANALYTICS
    # ══════════════════════════════════════
    total_outbound = len([t for t in processed if t["type"] == "outbound"])
    total_replied = len([t for t in processed if t["reply_detected"]])
    reply_rate = round((total_replied / total_outbound * 100), 1) if total_outbound > 0 else 0

    reply_days = [
        t["reply_time_days"] for t in processed
        if t["reply_time_days"] is not None
    ]
    avg_reply_time = round(sum(reply_days) / len(reply_days), 1) if reply_days else None

    category_counts = {}
    for t in processed:
        cat = t["reply_category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    analytics = {
        "total_outbound": total_outbound,
        "total_replied": total_replied,
        "reply_rate_pct": reply_rate,
        "avg_reply_time_days": avg_reply_time,
        "category_breakdown": category_counts,
    }

    return {"threads": processed, "analytics": analytics}
