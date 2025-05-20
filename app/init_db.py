from sqlalchemy.orm import Session
from app.modules.common.config.database import engine, Base, SessionLocal
from app.modules.users.models.user import User
from app.modules.users.schemas.user import UserCreate
from app.modules.users.services.user_service import create_user

def drop_all_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create test users
        test_users = [
            UserCreate(
                email="test1@example.com",
                username="testuser1",
                password="password123"
            ),
            UserCreate(
                email="test2@example.com",
                username="testuser2",
                password="password123"
            ),
            UserCreate(
                email="admin@example.com",
                username="admin",
                password="admin123"
            )
        ]
        
        for user_data in test_users:
            create_user(db, user_data)
            
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created") 