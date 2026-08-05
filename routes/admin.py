from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func
from models import db, User, Product, Category, Order, OrderItem, Service, ServiceBooking, CartItem, WishlistItem

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
    total_users = User.query.filter_by(is_admin=False).count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_bookings = ServiceBooking.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    pending_bookings = ServiceBooking.query.filter_by(status='pending').count()
    confirmed_bookings = ServiceBooking.query.filter_by(status='confirmed').count()
    completed_bookings = ServiceBooking.query.filter_by(status='completed').count()
    orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
    recent_bookings = ServiceBooking.query.order_by(ServiceBooking.created_at.desc()).limit(8).all()
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status.in_(['confirmed', 'shipped', 'delivered'])
    ).scalar() or 0
    total_wishlist = WishlistItem.query.count()
    active_carts = db.session.query(func.count(func.distinct(CartItem.user_id))).scalar() or 0
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           total_bookings=total_bookings,
                           pending_orders=pending_orders,
                           pending_bookings=pending_bookings,
                           confirmed_bookings=confirmed_bookings,
                           completed_bookings=completed_bookings,
                           orders=orders,
                           recent_bookings=recent_bookings,
                           total_revenue=total_revenue,
                           total_wishlist=total_wishlist,
                           active_carts=active_carts)


import re
from urllib.parse import parse_qs, urlparse, unquote


def clean_image_url(url_str):
    if not url_str:
        return ''
    url_str = url_str.strip()
    if 'google.' in url_str and 'imgres' in url_str:
        try:
            parsed = urlparse(url_str)
            qs = parse_qs(parsed.query)
            if 'imgurl' in qs:
                return unquote(qs['imgurl'][0])
        except Exception:
            pass
    return url_str


def generate_unique_slug(name, current_id=None):
    slug = re.sub(r'[^a-z0-9\s-]', '', (name or '').lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug) or 'product'

    base_slug = slug
    counter = 1
    query = Product.query.filter(Product.slug == slug)
    if current_id:
        query = query.filter(Product.id != current_id)

    while query.first():
        slug = f"{base_slug}-{counter}"
        counter += 1
        query = Product.query.filter(Product.slug == slug)
        if current_id:
            query = query.filter(Product.id != current_id)

    return slug


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
        try:
            name = request.form.get('name', '').strip()
            if not name:
                flash('Product name is required.', 'error')
                return render_template('admin/add_product.html', categories=categories)

            price_raw = request.form.get('price', '').strip()
            price = float(price_raw) if price_raw else 0.0

            disc_raw = request.form.get('discount_price', '').strip()
            discount_price = float(disc_raw) if disc_raw else None

            stock_raw = request.form.get('stock', '0').strip()
            stock = int(stock_raw) if stock_raw else 0

            img_url = clean_image_url(request.form.get('image_url', ''))
            cat_id = request.form.get('category_id', type=int)

            slug = generate_unique_slug(name)

            product = Product(
                name=name,
                slug=slug,
                description=request.form.get('description', '').strip(),
                price=price,
                discount_price=discount_price,
                image_url=img_url,
                stock=stock,
                category_id=cat_id if cat_id else None,
                is_featured=bool(request.form.get('is_featured')),
                is_active=True
            )
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'error')
            return render_template('admin/add_product.html', categories=categories)

    return render_template('admin/add_product.html', categories=categories)


@admin_bp.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    if request.method == 'POST':
        try:
            name = request.form.get('name', product.name).strip()
            if name:
                if name != product.name:
                    product.name = name
                    product.slug = generate_unique_slug(name, current_id=product.id)

            product.description = request.form.get('description', product.description).strip()

            price_raw = request.form.get('price', '').strip()
            if price_raw:
                product.price = float(price_raw)

            disc_raw = request.form.get('discount_price', '').strip()
            product.discount_price = float(disc_raw) if disc_raw else None

            img_url_raw = request.form.get('image_url', '').strip()
            product.image_url = clean_image_url(img_url_raw)

            stock_raw = request.form.get('stock', '').strip()
            if stock_raw:
                product.stock = int(stock_raw)

            cat_id = request.form.get('category_id', type=int)
            product.category_id = cat_id if cat_id else None

            product.is_featured = bool(request.form.get('is_featured'))
            product.is_active = bool(request.form.get('is_active', True))

            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')
            return render_template('admin/edit_product.html', product=product, categories=categories)

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


@admin_bp.route('/admin/users')
@admin_required
def users():
    search = request.args.get('q', '').strip()
    query = User.query.filter_by(is_admin=False)
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.username.ilike(f'%{search}%'))
        )
    all_users = query.order_by(User.created_at.desc()).all()

    # Enrich each user with quick counts
    user_data = []
    for u in all_users:
        order_count = Order.query.filter_by(user_id=u.id).count()
        booking_count = ServiceBooking.query.filter_by(user_id=u.id).count()
        cart_count = CartItem.query.filter_by(user_id=u.id).count()
        wishlist_count = WishlistItem.query.filter_by(user_id=u.id).count()
        total_spent = db.session.query(func.sum(Order.total_amount)).filter(
            Order.user_id == u.id,
            Order.status.in_(['confirmed', 'shipped', 'delivered'])
        ).scalar() or 0
        user_data.append({
            'user': u,
            'order_count': order_count,
            'booking_count': booking_count,
            'cart_count': cart_count,
            'wishlist_count': wishlist_count,
            'total_spent': total_spent,
        })

    return render_template('admin/users.html', user_data=user_data, search=search)


@admin_bp.route('/admin/users/<int:user_id>')
@admin_required
def customer_detail(user_id):
    user = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    bookings = ServiceBooking.query.filter_by(user_id=user_id).order_by(ServiceBooking.booking_date.desc()).all()
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    wishlist_items = WishlistItem.query.filter_by(user_id=user_id).all()
    total_spent = db.session.query(func.sum(Order.total_amount)).filter(
        Order.user_id == user_id,
        Order.status.in_(['confirmed', 'shipped', 'delivered'])
    ).scalar() or 0
    return render_template('admin/customer_detail.html',
                           user=user,
                           orders=orders,
                           bookings=bookings,
                           cart_items=cart_items,
                           wishlist_items=wishlist_items,
                           total_spent=total_spent)
