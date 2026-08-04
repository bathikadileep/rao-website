from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Product, Category, Order, Service, ServiceBooking

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    pending_bookings = ServiceBooking.query.filter_by(status='pending').count()
    orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
    total_revenue = sum(o.total_amount for o in orders if o.status in ('confirmed', 'shipped', 'delivered'))
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           pending_bookings=pending_bookings,
                           orders=orders,
                           total_revenue=total_revenue)


@admin_bp.route('/admin/products')
@admin_required
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        product = Product(
            name=name,
            slug=name.lower().replace(' ', '-').replace('&', 'and'),
            description=request.form.get('description', ''),
            price=float(request.form.get('price', 0)),
            discount_price=float(request.form.get('discount_price', 0)) or None,
            image_url=request.form.get('image_url', ''),
            stock=int(request.form.get('stock', 0)),
            category_id=request.form.get('category_id', type=int),
            is_featured=bool(request.form.get('is_featured')),
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_product.html', categories=categories)


@admin_bp.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form.get('name', product.name)
        product.description = request.form.get('description', product.description)
        product.price = float(request.form.get('price', product.price))
        dp = request.form.get('discount_price', '')
        product.discount_price = float(dp) if dp else None
        product.image_url = request.form.get('image_url', product.image_url)
        product.stock = int(request.form.get('stock', product.stock))
        product.category_id = request.form.get('category_id', type=int)
        product.is_featured = bool(request.form.get('is_featured'))
        product.is_active = bool(request.form.get('is_active', True))
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/edit_product.html', product=product, categories=categories)


@admin_bp.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    flash('Product deactivated.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/admin/orders')
@admin_required
def orders():
    status = request.args.get('status', '')
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, current_status=status)


@admin_bp.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status', order.status)
    db.session.commit()
    flash('Order status updated.', 'success')
    return redirect(url_for('admin.orders'))


@admin_bp.route('/admin/users')
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        cat = Category(
            name=name,
            slug=name.lower().replace(' ', '-'),
            description=request.form.get('description', ''),
            image_url=request.form.get('image_url', '')
        )
        db.session.add(cat)
        db.session.commit()
        flash('Category added!', 'success')
        return redirect(url_for('admin.categories'))
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/admin/categories/delete/<int:cat_id>', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/admin/services')
@admin_required
def services():
    services = Service.query.order_by(Service.created_at.desc()).all()
    return render_template('admin/services.html', services=services)


@admin_bp.route('/admin/services/add', methods=['GET', 'POST'])
@admin_required
def add_service():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        service = Service(
            name=name,
            slug=name.lower().replace(' ', '-').replace('&', 'and'),
            description=request.form.get('description', ''),
            price=float(request.form.get('price', 0)),
            estimated_time=request.form.get('estimated_time', '30 min'),
            image_icon=request.form.get('image_icon', 'fa-mobile-screen'),
        )
        db.session.add(service)
        db.session.commit()
        flash('Service added!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/add_service.html')


@admin_bp.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == 'POST':
        service.name = request.form.get('name', service.name)
        service.description = request.form.get('description', service.description)
        service.price = float(request.form.get('price', service.price))
        service.estimated_time = request.form.get('estimated_time', service.estimated_time)
        service.image_icon = request.form.get('image_icon', service.image_icon)
        service.is_active = bool(request.form.get('is_active', True))
        db.session.commit()
        flash('Service updated!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/edit_service.html', service=service)


@admin_bp.route('/admin/services/delete/<int:service_id>', methods=['POST'])
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    service.is_active = False
    db.session.commit()
    flash('Service deactivated.', 'success')
    return redirect(url_for('admin.services'))


@admin_bp.route('/admin/bookings')
@admin_required
def bookings():
    status = request.args.get('status', '')
    query = ServiceBooking.query
    if status:
        query = query.filter_by(status=status)
    bookings = query.order_by(ServiceBooking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings, current_status=status)


@admin_bp.route('/admin/bookings/<int:booking_id>/status', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    booking = ServiceBooking.query.get_or_404(booking_id)
    booking.status = request.form.get('status', booking.status)
    db.session.commit()
    flash('Booking status updated.', 'success')
    return redirect(url_for('admin.bookings'))
