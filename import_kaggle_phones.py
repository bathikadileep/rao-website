"""
Kaggle Dataset Importer — Mobile Phone Specifications and Prices
Dataset: pratikgarai/mobile-phone-specifications-and-prices
"""
import pandas as pd
import re
from app import app
from models import db, Product, Category

CSV_PATH = 'C:/Users/dilip/.cache/kagglehub/datasets/pratikgarai/mobile-phone-specifications-and-prices/versions/1/ndtv_data_final.csv'

# Brand → Unsplash image fallback
BRAND_IMAGES = {
    'Apple':    'https://images.unsplash.com/photo-1591337676887-a217a6970a8a?w=600&auto=format&fit=crop',
    'Samsung':  'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=600&auto=format&fit=crop',
    'OnePlus':  'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=600&auto=format&fit=crop',
    'Realme':   'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=600&auto=format&fit=crop',
    'Xiaomi':   'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop',
    'Vivo':     'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop',
    'Oppo':     'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600&auto=format&fit=crop',
    'LG':       'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=600&auto=format&fit=crop',
    'Motorola': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=600&auto=format&fit=crop',
    'Nokia':    'https://images.unsplash.com/photo-1567581935884-3349723552ca?w=600&auto=format&fit=crop',
    'default':  'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop',
}

def make_slug(name):
    slug = re.sub(r'[^a-z0-9\s-]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug

def make_description(row):
    parts = [f"{row['Name']} by {row['Brand']}."]
    if pd.notna(row.get('Battery capacity (mAh)')):
        parts.append(f"Battery: {int(row['Battery capacity (mAh)'])} mAh.")
    if pd.notna(row.get('Screen size (inches)')):
        parts.append(f"Screen: {row['Screen size (inches)']}\".")
    if pd.notna(row.get('RAM (MB)')):
        ram_gb = round(int(row['RAM (MB)']) / 1000, 1)
        parts.append(f"RAM: {ram_gb} GB.")
    if pd.notna(row.get('Internal storage (GB)')):
        parts.append(f"Storage: {int(row['Internal storage (GB)'])} GB.")
    if pd.notna(row.get('Rear camera')):
        parts.append(f"Rear camera: {row['Rear camera']} MP.")
    if pd.notna(row.get('Processor')):
        parts.append(f"Processor: {int(row['Processor'])}-core.")
    if pd.notna(row.get('Operating system')):
        parts.append(f"OS: {row['Operating system']}.")
    return ' '.join(parts)

with app.app_context():
    # Ensure Smartphones category
    cat = Category.query.filter_by(slug='smartphones').first()
    if not cat:
        cat = Category(name='Smartphones', slug='smartphones', description='Latest smartphones and accessories')
        db.session.add(cat)
        db.session.commit()

    df = pd.read_csv(CSV_PATH)
    df = df.dropna(subset=['Name', 'Price'])
    df = df[df['Price'] > 0]

    # Limit to top 50 phones (sorted by price desc = premium first)
    df = df.sort_values('Price', ascending=False).head(50)

    added = 0
    skipped = 0

    for _, row in df.iterrows():
        name = str(row['Name']).strip()
        if not name or name == 'nan':
            continue

        # Skip if already exists
        if Product.query.filter_by(name=name).first():
            skipped += 1
            continue

        price = float(row['Price'])
        # Add a small discount (8–18%) for display
        import random
        disc_pct = random.choice([0, 0, 5, 8, 10, 12, 15, 18])
        discount_price = round(price * (1 - disc_pct/100)) if disc_pct > 0 else None

        # Rating: simulate based on price tier
        if price > 80000:
            rating = round(random.uniform(4.3, 4.9), 1)
        elif price > 40000:
            rating = round(random.uniform(4.0, 4.6), 1)
        elif price > 15000:
            rating = round(random.uniform(3.7, 4.4), 1)
        else:
            rating = round(random.uniform(3.5, 4.2), 1)

        stock = random.choice([15, 20, 25, 30, 35, 40, 50])
        brand = str(row.get('Brand', '')).strip()
        image_url = BRAND_IMAGES.get(brand, BRAND_IMAGES['default'])

        slug = make_slug(name)
        base = slug
        n = 1
        while Product.query.filter_by(slug=slug).first():
            slug = base + '-' + str(n)
            n += 1

        description = make_description(row)

        product = Product(
            name=name,
            slug=slug,
            description=description,
            price=price,
            discount_price=discount_price,
            image_url=image_url,
            stock=stock,
            rating=rating,
            category_id=cat.id,
            is_featured=(price > 50000),
            is_active=True,
        )
        db.session.add(product)
        added += 1

    db.session.commit()
    print(f'DONE! Added={added} | Skipped={skipped}')
    print(f'Your shop now has phones ranging from budget to premium!')
