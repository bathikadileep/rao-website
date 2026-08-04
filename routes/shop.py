from flask import Blueprint, render_template, request
from flask_login import current_user
from models import Product, Category, WishlistItem

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/shop')
def shop():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category', '')
    search = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'newest')

    query = Product.query.filter_by(is_active=True)

    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    if search:
        query = query.filter(
            Product.name.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%')
        )

    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=10, error_out=False)
    categories = Category.query.all()

    return render_template('shop/shop.html',
                           products=products,
                           categories=categories,
                           current_category=category_slug,
                           search=search,
                           sort=sort)


@shop_bp.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = Product.query.filter_by(
        category_id=product.category_id,
        is_active=True
    ).filter(Product.id != product.id).limit(4).all()

    in_wishlist = False
    if current_user.is_authenticated and not current_user.is_admin:
        in_wishlist = WishlistItem.query.filter_by(
            user_id=current_user.id, product_id=product.id
        ).first() is not None

    return render_template('shop/product.html', product=product, related=related, in_wishlist=in_wishlist)

