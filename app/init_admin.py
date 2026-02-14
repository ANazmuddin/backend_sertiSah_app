from app.database import engine, SessionLocal
from app.models import AdminUser, Base
from app.auth import hash_password

def init():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    admin = db.query(AdminUser).filter_by(username="admin").first()

    if not admin:
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("admin123")
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created (admin / admin123)")
    else:
        print("ℹ️ Admin user already exists")

    db.close()

if __name__ == "__main__":
    init()
