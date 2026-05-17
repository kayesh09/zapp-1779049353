import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ext import db
from models import CartItem, Order, OrderItem, Product

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')


@checkout_bp.route('/', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty!', 'info')
        return redirect(url_for('products.catalog'))

    # Calculate total
    total = sum(item.get_total() for item in cart_items)

    if request.method == 'POST':
        try:
            # Create order first
            order = Order(
                user_id=current_user.id,
                total_amount=total,
                shipping_address=request.form.get('address'),
                shipping_city=request.form.get('city'),
                shipping_postal=request.form.get('postal'),
                phone=request.form.get('phone'),
                notes=request.form.get('notes'),
                status='pending',
                payment_status='pending'
            )
            order.order_number = order.generate_order_number()

            db.session.add(order)
            db.session.flush()  # <-- THIS IS THE FIX! Gets the ID without committing

            # Now create order items (order.id is now available)
            for cart_item in cart_items:
                if cart_item.quantity > cart_item.product.stock:
                    flash(f'Not enough stock for {cart_item.product.name}!', 'danger')
                    db.session.rollback()
                    return redirect(url_for('cart.view_cart'))

                order_item = OrderItem(
                    order_id=order.id,  # Now this has a value!
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price_at_time=cart_item.product.get_price()
                )
                db.session.add(order_item)

                # Update stock
                cart_item.product.stock -= cart_item.quantity

                # Remove from cart
                db.session.delete(cart_item)

            # Commit everything together
            db.session.commit()
            flash(f'Order placed successfully! Order number: {order.order_number}', 'success')
            return redirect(url_for('pages.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error placing order: {str(e)}', 'danger')
            return redirect(url_for('cart.view_cart'))

    return render_template('checkout.html',
                           cart_items=cart_items,
                           total=total,
                           user=current_user)