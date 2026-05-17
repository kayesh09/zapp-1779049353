import os
from app import app, db
from models import Product, Category

with app.app_context():
    # Check if we already have products
    if Product.query.count() == 0:
        print("Adding sample products...")

        # Get categories (assuming they exist)
        veg = Category.query.filter_by(slug='vegetables').first()
        fruit = Category.query.filter_by(slug='fruits').first()

        if not veg or not fruit:
            print("Categories not found. Please run the app first to create default categories.")
        else:
            products = [
                Product(
                    name="Fresh Tomato",
                    slug="fresh-tomato",
                    description="Fresh red tomatoes from local farms",
                    price=40.0,
                    stock=100,
                    category_id=veg.id,
                    featured=True
                ),
                Product(
                    name="Organic Banana",
                    slug="organic-banana",
                    description="Sweet and fresh bananas",
                    price=60.0,
                    stock=80,
                    category_id=fruit.id,
                    featured=True
                ),
                Product(
                    name="Fresh Carrot",
                    slug="fresh-carrot",
                    description="Crunchy orange carrots",
                    price=30.0,
                    stock=50,
                    category_id=veg.id
                ),
            ]

            for p in products:
                db.session.add(p)

            db.session.commit()
            print(f"✅ Added {len(products)} sample products!")
    else:
        print(f"✅ {Product.query.count()} products already exist.")