"""Database configuration shared by all SQLAlchemy models and services."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./email_agent.db"

# SQLite engine used across the application.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Factory for short-lived DB sessions in request/service code.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all SQLAlchemy ORM models inherit from.
Base = declarative_base()
