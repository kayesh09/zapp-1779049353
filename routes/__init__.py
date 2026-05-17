import os
# D:/PythonProject/gse/routes/__init__.py
"""
Routes package for GroceryHub
Contains all Flask blueprints for the application
"""

from .admin import admin_bp
from .auth import auth_bp
from .products import products_bp
from .cart import cart_bp
from .checkout import checkout_bp
from .pages import pages_bp

__all__ = [
    'admin_bp',
    'auth_bp',
    'products_bp',
    'cart_bp',
    'checkout_bp',
    'pages_bp',
]