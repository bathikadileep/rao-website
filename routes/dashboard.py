from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Order, ServiceBooking, WishlistItem

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    bookings = ServiceBooking.query.filter_by(user_id=current_user.id).order_by(ServiceBooking.created_at.desc()).all()
    total_spent = sum(o.total_amount for o in orders if o.status not in ('cancelled',))
    return render_template('dashboard/index.html',
                           orders=orders,
                           bookings=bookings,
                           total_spent=total_spent)


@dashboard_bp.route('/dashboard/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('dashboard/orders.html', orders=orders)


@dashboard_bp.route('/dashboard/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('dashboard/order_detail.html', order=order)


@dashboard_bp.route('/dashboard/services')
@login_required
def service_bookings():
    bookings = ServiceBooking.query.filter_by(user_id=current_user.id).order_by(ServiceBooking.created_at.desc()).all()
    return render_template('dashboard/service_bookings.html', bookings=bookings)
