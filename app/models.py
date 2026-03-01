from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String, unique=True, index=True)
    name = Column(String)
    nim = Column(String, index=True)
    program_studi = Column(String)
    institusi = Column(String)
    issue_date = Column(String)
    certificate_hash = Column(String, unique=True, index=True)
    blockchain_tx = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="ADMIN")  # <-- TAMBAHAN
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer)
    action = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)