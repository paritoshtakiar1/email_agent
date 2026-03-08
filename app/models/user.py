from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class User(Base):
    """Authenticated Gmail account and its OAuth token material."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

    # OAuth credentials required to rebuild Google API client credentials.
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_uri = Column(String)
    client_id = Column(String)
    client_secret = Column(String)
    # Comma-separated OAuth scopes granted by the user.
    scopes = Column(Text)
