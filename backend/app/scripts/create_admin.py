"""Script to create the initial admin user"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings


def create_admin():
    """Create the first superuser"""
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
        if existing_user:
            print(f"Admin user already exists: {settings.FIRST_SUPERUSER}")
            return
        
        # Create admin user
        admin = User(
            email=settings.FIRST_SUPERUSER,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="Admin User",
            is_superuser=True,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        
        print(f"Admin user created successfully: {settings.FIRST_SUPERUSER}")
        print(f"Password: {settings.FIRST_SUPERUSER_PASSWORD}")
        print("\nPlease change the password after first login!")
    
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
