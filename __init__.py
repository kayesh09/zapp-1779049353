import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)

    # Import models
    with app.app_context():
        from . import models
        db.create_all()

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.products import products_bp
    from .routes.cart import cart_bp
    from .routes.checkout import checkout_bp
    from .routes.admin import admin_bp
    from .routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(pages_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_cart_count():
        cart_count = 0
        if current_user.is_authenticated:
            from .models import Cart
            cart = Cart.query.filter_by(user_id=current_user.id).first()
            if cart:
                cart_count = len(cart.items)
        return {'cart_count': cart_count}

    @app.route('/')
    def index():
        from .models import Product, Category
        featured_products = Product.query.filter_by(featured=True).limit(6).all()
        categories = Category.query.all()
        return render_template('index.html', featured_products=featured_products, categories=categories)

    return app