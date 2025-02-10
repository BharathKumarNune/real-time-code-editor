from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from passlib.context import CryptContext
import os
from app.config import DATABASE_URL


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="viewer")  # Role field added
    code_files = relationship("CodeFile", back_populates="owner")
    sessions = relationship("EditingSession", back_populates="user")

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

class CodeFile(Base):
    __tablename__ = "code_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="code_files")
    sessions = relationship("EditingSession", back_populates="code_file")

class EditingSession(Base):
    __tablename__ = "editing_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code_file_id = Column(Integer, ForeignKey("code_files.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="sessions")
    code_file = relationship("CodeFile", back_populates="sessions")

class Suggestion(Base):
    __tablename__ = "suggestions"
    id = Column(String, primary_key=True, index=True)
    code = Column(String)
    suggestions = Column(String)
    status = Column(String, default="pending")


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
