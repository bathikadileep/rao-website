from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models import db, WishlistItem, Product

wishlist_bp = Blueprint('wishlist', __name__)


@wishlist_bp.route('/wishlist')
@login_required
def view_wishlist():
    items = WishlistItem.query.filter_by(user_id=current_user.id).order_by(WishlistItem.created_at.desc()).all()
    return render_template('wishlist/wishlist.html', items=items)


@wishlist_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    existing = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        in_wishlist = False
        message = f'{product.name} removed from wishlist.'
    else:
        item = WishlistItem(user_id=current_user.id, product_id=product_id)
        db.session.add(item)
        db.session.commit()
        in_wishlist = True
        message = f'{product.name} added to wishlist!'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count = WishlistItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'in_wishlist': in_wishlist, 'message': message, 'count': count})

    flash(message, 'success')
    return redirect(request.referrer or url_for('wishlist.view_wishlist'))


@wishlist_bp.route('/wishlist/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_wishlist(item_id):
    item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from wishlist.', 'success')
    return redirect(url_for('wishlist.view_wishlist'))


@wishlist_bp.route('/wishlist/count')
@login_required
def wishlist_count():
    count = WishlistItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})
