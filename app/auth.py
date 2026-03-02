from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models import AdminUser, AuditLog


# ==========================================================
# PASSWORD CONTEXT
# ==========================================================

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


# ==========================================================
# DATABASE DEPENDENCY
# ==========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================================
# PASSWORD UTILITIES
# ==========================================================

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ==========================================================
# AUTHENTICATION
# ==========================================================

def authenticate_admin(username: str, password: str, db: Session):
    user = db.query(AdminUser).filter(
        AdminUser.username == username
    ).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


# ==========================================================
# LOGIN REQUIRED (Session Check)
# ==========================================================

def login_required(request: Request):
    admin_id = request.session.get("admin_id")

    if not admin_id:
        return RedirectResponse("/login", status_code=302)

    return None


# ==========================================================
# GET CURRENT USER FROM SESSION
# ==========================================================

def get_current_user(request: Request):
    admin_id = request.session.get("admin_id")

    if not admin_id:
        return None

    db = SessionLocal()
    user = db.query(AdminUser).filter(
        AdminUser.id == admin_id
    ).first()
    db.close()

    return user


# ==========================================================
# ROLE REQUIRED (RBAC)
# ==========================================================

def role_required(allowed_roles: list):
    def checker(request: Request):

        admin_role = request.session.get("admin_role")

        if not admin_role:
            return RedirectResponse("/login", status_code=302)

        if admin_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Anda tidak memiliki izin untuk mengakses halaman ini"
            )

        return None

    return checker


# ==========================================================
# AUDIT LOG CREATOR
# ==========================================================

def create_audit_log(
    db: Session,
    admin_id: int,
    action: str,
    description: str = "",
    ip_address: str = None
):
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        description=description,
        ip_address=ip_address,
        created_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()