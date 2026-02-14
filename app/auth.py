from fastapi import Request
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AdminUser

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# ===== DATABASE UTILS =====

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== PASSWORD UTILS =====

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(password):
    return pwd_context.hash(password)

# ===== AUTH =====

def authenticate_admin(username: str, password: str, db: Session):
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def require_login(request: Request):
    if not request.session.get("admin_id"):
        return RedirectResponse("/login", status_code=302)
