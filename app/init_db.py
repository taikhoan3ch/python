from sqlalchemy.orm import Session
from app.modules.common.config.database import engine, Base, SessionLocal
from app.modules.users.models.user import User
from app.modules.users.schemas.user import UserCreate
from app.modules.users.services.user_service import create_user
from app.modules.users.services.role_service import RoleService

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Initialize roles and permissions
        RoleService.initialize_default_roles_and_permissions(db)
        
        # Create test users with different roles
        test_users = [
            UserCreate(
                email="admin@example.com",
                username="admin",
                password="admin123",
                role_id=1  # Admin role
            ),
            UserCreate(
                email="manager@example.com",
                username="manager",
                password="manager123",
                role_id=2  # Manager role
            ),
            UserCreate(
                email="user@example.com",
                username="user",
                password="user123",
                role_id=3  # Regular user role
            )
        ]
        
        for user_data in test_users:
            try:
                create_user(db, user_data)
            except Exception as e:
                print(f"Error creating user {user_data.email}: {str(e)}")
            
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization completed!") 