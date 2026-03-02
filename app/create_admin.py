from app.database import SessionLocal
from app.models import AdminUser
from app.auth import hash_password

def create_admin(username, password):

    db = SessionLocal()

    existing = db.query(AdminUser).filter(
        AdminUser.username == username
    ).first()

    if existing:
        print("User sudah ada.")
        db.close()
        return

    new_user = AdminUser(
        username=username,
        password_hash=hash_password(password),
        role="ADMIN"
    )

    db.add(new_user)
    db.commit()
    db.close()

    print("ADMIN berhasil dibuat!")

if __name__ == "__main__":
    create_admin("adminbiasa", "admin123")