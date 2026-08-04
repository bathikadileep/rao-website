from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, CartItem, Product

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/cart')
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum((item.product.discount_price or item.product.price) * item.quantity for item in items)
    shipping = 0 if subtotal >= 500 else 49
    total = subtotal + shipping
    return render_template('shop/cart.html', items=items, subtotal=subtotal, shipping=shipping, total=total)


@cart_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)

    if not product_id:
        flash('Invalid product.', 'error')
        return redirect(url_for('shop.shop'))

    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        flash('Product not found.', 'error')
        return redirect(url_for('shop.shop'))

    if product.stock < quantity:
        flash('Not enough stock available.', 'error')
        return redirect(url_for('shop.product_detail', slug=product.slug))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    flash('Added to cart!', 'success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Added to cart!'})

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    item_id = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)

    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        if quantity <= 0:
            db.session.delete(item)
        else:
            item.quantity = quantity
        db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    item_id = request.form.get('item_id', type=int)
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from cart.', 'success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/count')
@login_required
def cart_count():
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})
