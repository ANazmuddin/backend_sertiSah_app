from app.database import SessionLocal
from app.models import AuditLog

def log_action(admin_id: int, action: str, description: str):
    db = SessionLocal()

    log = AuditLog(
        admin_id=admin_id,
        action=action,
        description=description
    )

    db.add(log)
    db.commit()
    db.close()