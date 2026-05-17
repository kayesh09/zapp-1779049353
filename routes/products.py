import os
from flask import Blueprint, render_template, request
from models import Product, Category
from sqlalchemy import or_
from ext import db

products_bp = Blueprint('products', __name__, url_prefix='/products')


@products_bp.route('/')
def catalog():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    search_query = request.args.get('q')
    sort = request.args.get('sort', 'newest')

    query = Product.query.filter_by(is_active=True)

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)

    if search_query:
        query = query.filter(or_(
            Product.name.ilike(f'%{search_query}%'),
            Product.description.ilike(f'%{search_query}%')
        ))

    # Sorting
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=12, error_out=False)

    return render_template('product_catalog.html',
                           products=products,
                           category_slug=category_slug,
                           search_query=search_query,
                           sort=sort)


@products_bp.route('/<slug>')
def detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related_products = Product.query.filter_by(
        category_id=product.category_id,
        is_active=True
    ).filter(Product.id != product.id).limit(4).all()

    return render_template('product_detail.html',
                           product=product,
                           related_products=related_products)