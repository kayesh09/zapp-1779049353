import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from ext import db
from models import Category

app = create_app()
with app.app_context():
    # Check if already exists
    if Category.query.first():
        print("Categories already exist!")
    else:
        categories = [
            Category(name='Fresh Fruits', slug='fresh-fruits', description='Fresh organic fruits'),
            Category(name='Vegetables', slug='vegetables', description='Farm fresh vegetables'),
            Category(name='Dairy & Eggs', slug='dairy-eggs', description='Milk, cheese and eggs'),
            Category(name='Bakery', slug='bakery', description='Fresh bread and pastries'),
            Category(name='Beverages', slug='beverages', description='Drinks and juices'),
            Category(name='Snacks', slug='snacks', description='Healthy snacks')
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
        print("✅ 6 categories created! Now refresh the Add Product page.")