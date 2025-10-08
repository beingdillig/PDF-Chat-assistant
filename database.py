"""Database models and connection."""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:8287@localhost:5432/postgres")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Document(Base):
    """Store PDF document metadata."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), index=True)
    filename = Column(String(500))
    filepath = Column(String(1000))
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    status = Column(String(50), default="processing")
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    """Store chat messages."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), index=True)
    role = Column(String(50))  # user or assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()