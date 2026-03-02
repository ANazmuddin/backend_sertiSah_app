from app.database import SessionLocal
from app.models import AdminUser
from app.auth import hash_password

def create_superadmin():

    db = SessionLocal()

    existing = db.query(AdminUser).filter(
        AdminUser.username == "superadmin"
    ).first()

    if existing:
        print("Superadmin sudah ada.")
        db.close()
        return

    new_user = AdminUser(
        username="superadmin",
        password_hash=hash_password("password123"),
        role="SUPERADMIN"
    )

    db.add(new_user)
    db.commit()
    db.close()

    print("SUPERADMIN berhasil dibuat!")

if __name__ == "__main__":
    create_superadmin()