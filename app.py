import os
import stripe
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
with app.app_context():
    db.create_all()

CORS(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

stripe.api_key = app.config.get('STRIPE_SECRET_KEY')


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


from routes.auth import auth_bp
from routes.shop import shop_bp
from routes.cart import cart_bp
from routes.checkout import checkout_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp
from routes.services import services_bp
from api.main import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(checkout_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(services_bp)
app.register_blueprint(api_bp, url_prefix='/api')


from flask import request

@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        response.headers['Accept-Ranges'] = 'bytes'
    return response


@app.route('/')
def index():
    from flask import render_template
    from models import Product, Category, Service
    featured = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    categories = Category.query.all()
    services = Service.query.filter_by(is_active=True).limit(4).all()
    return render_template('index.html', featured=featured, categories=categories, services=services, is_location_page=False)


@app.route('/location')
def location_page():
    from flask import render_template
    from models import Product, Category, Service
    featured = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    categories = Category.query.all()
    services = Service.query.filter_by(is_active=True).limit(4).all()
    return render_template('index.html', featured=featured, categories=categories, services=services, is_location_page=True)


@app.template_filter('format_price')
def format_price(value):
    return f"₹{value:,.2f}"


@app.template_filter('format_date')
def format_date(value):
    return value.strftime('%d %b %Y')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
