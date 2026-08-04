from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False, default='')
    phone = db.Column(db.String(20), default='')
    address = db.Column(db.Text, default='')
    city = db.Column(db.String(80), default='')
    state = db.Column(db.String(80), default='')
    pincode = db.Column(db.String(10), default='')
    is_admin = db.Column(db.Boolean, default=False)
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    service_bookings = db.relationship('ServiceBooking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    image_url = db.Column(db.String(500), default='')

    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(500), default='')
    stock = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship('Product', backref='cart_entries')


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='pending')
    shipping_name = db.Column(db.String(120), default='')
    shipping_address = db.Column(db.Text, default='')
    shipping_city = db.Column(db.String(80), default='')
    shipping_state = db.Column(db.String(80), default='')
    shipping_pincode = db.Column(db.String(10), default='')
    shipping_phone = db.Column(db.String(20), default='')
    payment_id = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship('Product')


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, nullable=False)
    estimated_time = db.Column(db.String(50), default='30 min')
    image_icon = db.Column(db.String(50), default='fa-mobile-screen')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    bookings = db.relationship('ServiceBooking', backref='service', lazy=True)


class ServiceBooking(db.Model):
    __tablename__ = 'service_bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    phone_model = db.Column(db.String(120), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text, default='')
    status = db.Column(db.String(30), default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
