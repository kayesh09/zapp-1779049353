import os
from app import app, db
from models import Product, Category

with app.app_context():
    # Check how many products we have
    product_count = Product.query.count()
    print(f"Current products in database: {product_count}")

    if product_count == 0:
        print("Adding sample products...")

        # Get or create categories
        veg = Category.query.filter_by(slug='vegetables').first()
        if not veg:
            veg = Category(name='Vegetables', slug='vegetables', description='Fresh vegetables')
            db.session.add(veg)
            db.session.commit()

        fruit = Category.query.filter_by(slug='fruits').first()
        if not fruit:
            fruit = Category(name='Fruits', slug='fruits', description='Fresh fruits')
            db.session.add(fruit)
            db.session.commit()

        # Add sample products
        sample_products = [
            Product(name="Fresh Tomato", slug="fresh-tomato", price=45.0, stock=100, category_id=veg.id, featured=True, description="Juicy red tomatoes"),
            Product(name="Organic Banana", slug="organic-banana", price=65.0, stock=80, category_id=fruit.id, featured=True, description="Sweet ripe bananas"),
            Product(name="Fresh Carrot", slug="fresh-carrot", price=35.0, stock=60, category_id=veg.id, description="Crunchy carrots"),
            Product(name="Green Apple", slug="green-apple", price=90.0, stock=50, category_id=fruit.id, description="Fresh green apples"),
        ]

        for p in sample_products:
            db.session.add(p)

        db.session.commit()
        print("✅ 4 sample products added successfully!")
    else:
        print(f"✅ You already have {product_count} products.")

    # Show all products
    print("\nAll products:")
    for p in Product.query.all():
        print(f"- {p.name} | Slug: {p.slug} | Price: ₹{p.price}")