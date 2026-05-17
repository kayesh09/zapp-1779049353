import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from ext import db
from models import User, Category, Product
from werkzeug.security import generate_password_hash


def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()

        # Create all tables
        db.create_all()

        print("Database initialized successfully!")


def create_admin():
    app = create_app()
    with app.app_context():
        # Create admin user
        admin = User(
            username='admin',
            email='admin@freshmart.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')

        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@freshmart.com / admin123")


if __name__ == '__main__':
    init_db()
    create_admin()