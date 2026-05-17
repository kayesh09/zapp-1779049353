import os
from flask import Blueprint, render_template
from models import Product, Category

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    featured_products = Product.query.filter_by(is_active=True, is_featured=True).limit(8).all()
    new_arrivals = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(4).all()
    categories = Category.query.filter_by(is_active=True).limit(6).all()
    return render_template('index.html',
                         featured_products=featured_products,
                         new_arrivals=new_arrivals,
                         categories=categories)

@pages_bp.route('/about')
def about():
    return render_template('pages/about.html')

@pages_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle contact form
        pass
    return render_template('pages/contact.html')

@pages_bp.route('/faq')
def faq():
    return render_template('pages/faq.html')

@pages_bp.route('/privacy')
def privacy():
    return render_template('pages/privacy.html')

@pages_bp.route('/terms')
def terms():
    return render_template('pages/terms.html')