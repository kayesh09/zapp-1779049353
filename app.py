import os
from flask import Flask, render_template
from ext import db, login_manager,csrf
from models import User, Category, Product, CartItem, Order, OrderItem


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # HARD CODED CONFIG - No external files needed
    app.config['SECRET_KEY'] = 'your-super-secret-key-here-12345'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///site.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images', 'products')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Ensure folders exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    upload_folder = os.path.join(app.static_folder, 'images', 'products')
    os.makedirs(upload_folder, exist_ok=True)

    app.config['WTF_CSRF_ENABLED'] = True
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.pages import pages_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.checkout import checkout_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(admin_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Context processors
    @app.context_processor
    def inject_categories():
        categories = Category.query.filter_by(is_active=True).all()
        return dict(categories=categories)

    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return dict(user=current_user, current_user=current_user)

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)