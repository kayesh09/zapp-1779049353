from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from ext import db
from models import User, Category, Product, Order
import os
import random
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('pages.index'))
        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def generate_unique_slug(base_slug):
    """Generate a unique slug by appending numbers if needed"""
    slug = base_slug.lower().replace(' ', '-')
    unique_slug = slug
    counter = 1

    while Product.query.filter_by(slug=unique_slug).first():
        unique_slug = f"{slug}-{counter}"
        counter += 1

    return unique_slug


def generate_unique_sku(base_sku):
    """Generate a unique SKU by appending numbers if needed"""
    if not base_sku:
        return None

    unique_sku = base_sku.upper()
    counter = 1

    while Product.query.filter_by(sku=unique_sku).first():
        unique_sku = f"{base_sku.upper()}-{counter:03d}"
        counter += 1

    return unique_sku


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock < 10).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           recent_orders=recent_orders,
                           low_stock=low_stock)


@admin_bp.route('/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/products.html', products=products)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        slug_input = request.form.get('slug')
        sku_input = request.form.get('sku')

        # Generate unique slug
        base_slug = slug_input if slug_input else name.lower().replace(' ', '-').replace("'", "")
        unique_slug = generate_unique_slug(base_slug)

        # Generate unique SKU (or None if empty)
        unique_sku = generate_unique_sku(sku_input) if sku_input else None

        product = Product(
            name=name,
            slug=unique_slug,
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            discount_price=float(request.form.get('discount_price')) if request.form.get('discount_price') else None,
            stock=int(request.form.get('stock')),
            unit=request.form.get('unit') or 'piece',
            sku=unique_sku,
            category_id=int(request.form.get('category_id')),
            is_active=request.form.get('is_active') == 'on',
            is_featured=request.form.get('is_featured') == 'on'
        )

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{product.slug}_{file.filename}")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                product.image_url = f'products/{filename}'

        db.session.add(product)
        db.session.commit()
        flash(f'Product added successfully! Slug: {unique_slug}, SKU: {unique_sku or "None"}', 'success')
        return redirect(url_for('admin.products'))

    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        name = request.form.get('name')
        slug_input = request.form.get('slug')
        sku_input = request.form.get('sku')

        # Only generate new slug if it's different and already taken
        new_slug = slug_input.lower().replace(' ', '-').replace("'", "")
        if new_slug != product.slug and Product.query.filter_by(slug=new_slug).first():
            new_slug = generate_unique_slug(new_slug)

        # Only generate new SKU if it's different and already taken
        new_sku = sku_input.upper() if sku_input else None
        if new_sku and new_sku != product.sku and Product.query.filter_by(sku=new_sku).first():
            new_sku = generate_unique_sku(sku_input)

        product.name = name
        product.slug = new_slug
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.discount_price = float(request.form.get('discount_price')) if request.form.get(
            'discount_price') else None
        product.stock = int(request.form.get('stock'))
        product.unit = request.form.get('unit') or 'piece'
        product.sku = new_sku
        product.category_id = int(request.form.get('category_id'))
        product.is_active = request.form.get('is_active') == 'on'
        product.is_featured = request.form.get('is_featured') == 'on'

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Delete old image if exists
                if product.image_url:
                    try:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                                product.image_url.replace('products/', ''))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except:
                        pass

                filename = secure_filename(f"{product.slug}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                product.image_url = f'products/{filename}'

        db.session.commit()
        flash(f'Product updated! Slug: {new_slug}, SKU: {new_sku or "None"}', 'success')
        return redirect(url_for('admin.products'))

    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    # Delete image file if exists
    if product.image_url:
        try:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_url.replace('products/', ''))
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def categories():
    if request.method == 'POST':
        category = Category(
            name=request.form.get('name'),
            slug=request.form.get('slug'),
            description=request.form.get('description')
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added!', 'success')
        return redirect(url_for('admin.categories'))

    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')

    query = Order.query
    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/orders/<int:order_id>/update', methods=['POST'])
@login_required
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status')
    db.session.commit()
    flash('Order status updated!', 'success')
    return redirect(url_for('admin.orders'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)