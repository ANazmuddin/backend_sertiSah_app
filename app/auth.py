from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AdminUser

# ================= PASSWORD CONTEXT =================

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# ================= DATABASE DEPENDENCY =================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= PASSWORD UTILS =================

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ================= AUTHENTICATION =================

def authenticate_admin(username: str, password: str, db: Session):
    user = db.query(AdminUser).filter(AdminUser.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user

# ================= LOGIN REQUIRED DEPENDENCY =================

def login_required(request: Request):
    admin_id = request.session.get("admin_id")

    if not admin_id:
        return RedirectResponse("/login", status_code=302)

    return None
