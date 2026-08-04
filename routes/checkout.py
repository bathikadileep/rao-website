import stripe
try:
    import razorpay
except ImportError:
    razorpay = None
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import db, CartItem, Order, OrderItem

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('shop.shop'))

    subtotal = sum((item.product.discount_price or item.product.price) * item.quantity for item in items)
    shipping = 0 if subtotal >= 500 else 49
    total = subtotal + shipping

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'cod')
        
        order = Order(
            user_id=current_user.id,
            total_amount=total,
            shipping_name=request.form.get('full_name', current_user.full_name or current_user.username),
            shipping_address=request.form.get('address', current_user.address or ''),
            shipping_city=request.form.get('city', current_user.city or 'Narasaraopet'),
            shipping_state=request.form.get('state', current_user.state or 'Andhra Pradesh'),
            shipping_pincode=request.form.get('pincode', current_user.pincode or '522601'),
            shipping_phone=request.form.get('phone', current_user.phone or '7386738665'),
            status='confirmed' if payment_method == 'cod' else 'pending'
        )

        for item in items:
            order_item = OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.discount_price or item.product.price
            )
            order.items.append(order_item)
            item.product.stock -= item.quantity

        db.session.add(order)
        for item in items:
            db.session.delete(item)
        db.session.commit()

        flash('Order created successfully!', 'success')
        return redirect(url_for('checkout.order_confirmation', order_id=order.id))

    razorpay_key_id = current_app.config.get('RAZORPAY_KEY_ID', 'rzp_test_placeholder')
    return render_template('shop/checkout.html', items=items, subtotal=subtotal, shipping=shipping, total=total, razorpay_key_id=razorpay_key_id)


@checkout_bp.route('/checkout/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('shop/confirmation.html', order=order)


@checkout_bp.route('/order/<int:order_id>/invoice')
@login_required
def generate_invoice(order_id):
    order = Order.query.filter_by(id=order_id).first_or_404()
    # Allow order owner or admin to access invoice
    if order.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        flash('Unauthorized access to invoice.', 'error')
        return redirect(url_for('index'))
    return render_template('shop/invoice.html', order=order)


@checkout_bp.route('/create-razorpay-order', methods=['POST'])
@login_required
def create_razorpay_order():
    try:
        data = request.get_json() or {}
        amount = float(data.get('amount', 0))
        amount_in_paise = int(amount * 100)

        key_id = current_app.config.get('RAZORPAY_KEY_ID')
        key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')

        if key_id and key_id != 'rzp_test_placeholder' and key_secret != 'rzp_secret_placeholder':
            client = razorpay.Client(auth=(key_id, key_secret))
            rzp_order = client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1
            })
            return jsonify({
                'id': rzp_order['id'],
                'amount': rzp_order['amount'],
                'currency': rzp_order['currency'],
                'key': key_id
            })
        else:
            # Fallback test order mode
            return jsonify({
                'id': f"order_test_{current_user.id}_{int(amount)}",
                'amount': amount_in_paise,
                'currency': 'INR',
                'key': key_id or 'rzp_test_demo'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@checkout_bp.route('/verify-razorpay-payment', methods=['POST'])
@login_required
def verify_razorpay_payment():
    try:
        data = request.get_json() or {}
        order_id = data.get('order_id')
        payment_id = data.get('razorpay_payment_id')

        if order_id:
            order = Order.query.filter_by(id=int(order_id), user_id=current_user.id).first()
            if order:
                order.status = 'confirmed'
                db.session.commit()
                return jsonify({'status': 'success', 'redirect_url': url_for('checkout.order_confirmation', order_id=order.id)})
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@checkout_bp.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    try:
        data = request.get_json()
        amount = int(float(data.get('amount', 0)) * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='inr',
            metadata={'user_id': current_user.id}
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
