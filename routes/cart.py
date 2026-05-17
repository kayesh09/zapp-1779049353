import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ext import db
from models import CartItem, Product

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


@cart_bp.route('/')
def view_cart():
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    else:
        cart_items = []
        # Handle session-based cart for guests
    return render_template('cart.html', cart_items=cart_items)


@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    if not product.is_in_stock():
        flash('Product is out of stock!', 'danger')
        return redirect(url_for('products.detail', slug=product.slug))

    if quantity > product.stock:
        flash(f'Only {product.stock} items available!', 'danger')
        return redirect(url_for('products.detail', slug=product.slug))

    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    quantity = int(request.form.get('quantity', 1))

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        if quantity > cart_item.product.stock:
            return jsonify({'error': 'Not enough stock'}), 400
        cart_item.quantity = quantity

    db.session.commit()

    # Calculate new totals
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.get_total() for item in cart_items)
    count = sum(item.quantity for item in cart_items)

    return jsonify({
        'item_total': cart_item.get_total() if quantity > 0 else 0,
        'cart_total': total,
        'cart_count': count
    })


@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('cart.view_cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart!', 'success')
    return redirect(url_for('cart.view_cart'))