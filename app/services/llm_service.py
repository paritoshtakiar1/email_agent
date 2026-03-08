"""LLM-backed helpers for reply classification and draft generation."""

import json
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def llm_classify(text: str):
    """Classify inbound email text into one pipeline category.

    Args:
        text: Email body (or cleaned excerpt) to classify.

    Returns:
        Category string such as ``positive`` or ``unsubscribe``.
        Falls back to ``neutral`` on parse/API errors.
    """
    try:
        prompt = f"""You are an expert email classifier for a sales/outreach team.

Classify this email reply into exactly ONE of these categories:

- positive - They expressed interest, said yes, want to learn more, or are open to next steps
- negative - They declined, said no, not interested, or already have a solution
- requesting_more_info - They asked for more details, case studies, pricing, or specifics before deciding
- out_of_office - Auto-reply indicating they are away, on vacation, or unavailable
- wrong_person - They said they're not the right contact and may have redirected to someone else
- unsubscribe - if it is a promotional/irrelevant mail.

Respond ONLY with valid JSON. No explanation, no markdown.
Format: {{"reply_category": "category_name"}}

Email to classify:
\"\"\"{text}\"\"\"
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You classify email replies into exact categories. Output only JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        # Some models wrap JSON in markdown fences; strip them before parsing.
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        parsed = json.loads(content)
        return parsed.get("reply_category", "neutral")
    except Exception:
        return "neutral"


def generate_followup(original_email: str, stage: int):
    """Generate a follow-up for an outbound thread with no reply yet.

    Args:
        original_email: The first outbound message sent by the user.
        stage: Follow-up number (1, 2, or 3).

    Returns:
        Draft email body string, or None when stage is invalid/API fails.
    """
    try:
        if stage == 1:
            instruction = """Write a friendly follow-up that:
- References the original email naturally (don't just say "following up")
- Adds one new small insight or value point they might care about
- Ends with a soft, low-pressure ask (not "let me know if interested")
- Feels like a real person checking in, not a sequence"""
        elif stage == 2:
            instruction = """Write a second follow-up that:
- Takes a completely different angle from the first follow-up
- Leads with a relevant insight, trend, or question about their industry
- Connects that back to how you could help
- Keeps it conversational and curious, not salesy
- Ends with a specific but easy ask (e.g. "worth a 10-min chat?")"""
        elif stage == 3:
            instruction = """Write a final follow-up that:
- Acknowledges this is your last message (without guilt-tripping)
- Is the shortest of all three (2-3 sentences max)
- Gives them an easy out ("totally understand if the timing isn't right")
- Leaves the door open without being pushy
- Feels respectful and human"""
        else:
            return None

        prompt = f"""You are a skilled outreach specialist writing a follow-up email.

Original email that was sent:
\"\"\"{original_email}\"\"\"

Your task:
{instruction}

Hard rules:
- Maximum 3-5 sentences
- Sound like a real human, not a template or AI
- Do NOT start with "I hope this email finds you well" or any cliche opener
- Do NOT repeat the original email content
- Do NOT include a subject line
- Do NOT use placeholder text like [Name] or [Company]
- Just output the email body, nothing else"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You write concise, natural outreach follow-ups that sound like a real person wrote them. You never use templates or cliches.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def generate_reply(original_email: str, reply_email: str, reply_category: str = "requesting_more_info"):
    """Generate a context-aware reply draft for categorized inbound responses.

    Supported categories: ``positive``, ``requesting_more_info``, ``negative``,
    ``wrong_person``.

    Args:
        original_email: Initial outbound email content (may be empty for inbound threads).
        reply_email: Latest inbound message content.
        reply_category: Pre-classified category to condition tone/intent.

    Returns:
        Reply email body string, or None if category is unsupported/API fails.
    """
    try:
        instructions = {
            "positive": """The lead expressed interest or said yes.
Write a reply that:
- Thanks them warmly (but briefly - one line, not gushing)
- Suggests scheduling a call or meeting as the clear next step
- Offers 2-3 specific time slots or asks for their availability
- Keeps momentum - don't let it cool down
- Tone: enthusiastic but professional, like a colleague not a salesperson""",
            "requesting_more_info": """The lead asked for more details before deciding.
Write a reply that:
- Directly addresses what they asked about (reference their specific question)
- Provides 2-3 concrete points of value or key details
- Keeps it scannable - short paragraphs or a brief list is fine
- Ends by suggesting a quick call to walk through details live
- Tone: helpful and knowledgeable, not pushy""",
            "negative": """The lead declined or said they're not interested.
Write a reply that:
- Accepts their decision gracefully (no arguing or objection handling)
- Thanks them genuinely for their time and response
- Leaves the door open for the future in one sentence
- Is SHORT - 2-3 sentences maximum
- Tone: professional, respectful, zero pressure
- Do NOT try to convince them or offer alternatives""",
            "wrong_person": """The lead said they're not the right person for this.
Write a reply that:
- Thanks them for letting you know
- If they mentioned a specific person to contact, reference that person by name
- Asks if they could make a warm intro or if you should reach out directly
- Keeps it brief - 2-3 sentences
- Tone: appreciative and respectful of their time""",
        }

        instruction = instructions.get(reply_category)
        if not instruction:
            return None

        prompt = f"""You are writing a professional reply to someone who responded to an outreach email.

Original outreach email you sent:
\"\"\"{original_email}\"\"\"

Their reply:
\"\"\"{reply_email}\"\"\"

Your task:
{instruction}

Hard rules:
- Sound like a real human, not a template
- Do NOT start with "Thank you for getting back to me" or similar cliche
- Do NOT repeat their message back to them
- Do NOT include a subject line
- Do NOT use placeholder text like [Name] or [Company]
- Just output the email body, nothing else"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You write natural, context-aware business email replies. You match your tone to the situation - warm for positive replies, graceful for rejections, helpful for info requests.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None
