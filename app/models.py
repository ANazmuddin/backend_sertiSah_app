from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

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