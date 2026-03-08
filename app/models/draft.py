from sqlalchemy import Column, String, Integer
from app.core.database import Base


class Draft(Base):
    """Per-thread cache for draft lifecycle and reply-classification metadata."""

    __tablename__ = "drafts"

    # Gmail thread ID is used as the stable primary key for this cache row.
    thread_id = Column(String, primary_key=True)
    # Gmail draft ID for the currently unsent draft, if one exists.
    draft_id = Column(String, nullable=True)
    # Last classified category for this thread's latest inbound message.
    reply_category = Column(String, nullable=True)
    # Message count at the moment reply_category was computed.
    message_count = Column(Integer, nullable=True)
    # State key the latest draft was generated for (used for de-duplication).
    draft_generated_for = Column(String, nullable=True)
