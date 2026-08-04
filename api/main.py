from flask import Blueprint, jsonify, request
from models import Product, Category, Order, User, Service, ServiceBooking

api_bp = Blueprint('api', __name__)


@api_bp.route('/products')
def api_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    products = Product.query.filter_by(is_active=True).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'price': p.price,
            'discount_price': p.discount_price,
            'image_url': p.image_url,
            'rating': p.rating,
            'stock': p.stock,
            'category': p.category.name if p.category else None
        } for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    })


@api_bp.route('/products/<slug>')
def api_product_detail(slug):
    p = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    return jsonify({
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'description': p.description,
        'price': p.price,
        'discount_price': p.discount_price,
        'image_url': p.image_url,
        'rating': p.rating,
        'stock': p.stock,
        'category': p.category.name if p.category else None
    })


@api_bp.route('/categories')
def api_categories():
    cats = Category.query.all()
    return jsonify({
        'categories': [{'id': c.id, 'name': c.name, 'slug': c.slug} for c in cats]
    })


@api_bp.route('/orders/<int:order_id>')
def api_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        'id': order.id,
        'status': order.status,
        'total_amount': order.total_amount,
        'created_at': order.created_at.isoformat(),
        'items': [{
            'product': item.product.name,
            'quantity': item.quantity,
            'price': item.price
        } for item in order.items]
    })


@api_bp.route('/services')
def api_services():
    services = Service.query.filter_by(is_active=True).all()
    return jsonify({
        'services': [{
            'id': s.id,
            'name': s.name,
            'slug': s.slug,
            'description': s.description,
            'price': s.price,
            'estimated_time': s.estimated_time,
            'icon': s.image_icon
        } for s in services]
    })


@api_bp.route('/services/<slug>')
def api_service_detail(slug):
    s = Service.query.filter_by(slug=slug, is_active=True).first_or_404()
    return jsonify({
        'id': s.id,
        'name': s.name,
        'slug': s.slug,
        'description': s.description,
        'price': s.price,
        'estimated_time': s.estimated_time,
        'icon': s.image_icon
    })
