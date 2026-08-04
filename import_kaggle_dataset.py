import os
import sys
import re
import pandas as pd
import kagglehub

sys.path.insert(0, os.path.dirname(__file__))
from app import app
from models import db, Category, Product, Service

# High-Quality PNG Mobile Image Mapping by Brand/Model
BRAND_IMAGE_MAP = {
    'apple': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80&fm=png',
    'samsung': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=80&fm=png',
    'oneplus': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80&fm=png',
    'google': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80&fm=png',
    'xiaomi': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop&q=80&fm=png',
    'realme': 'https://images.unsplash.com/photo-1546054454-aa26e2b734c7?w=600&auto=format&fit=crop&q=80&fm=png',
    'vivo': 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600&auto=format&fit=crop&q=80&fm=png',
    'oppo': 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&auto=format&fit=crop&q=80&fm=png',
    'motorola': 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600&auto=format&fit=crop&q=80&fm=png',
    'default': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop&q=80&fm=png'
}

# High-Quality PNG Images for Visiting Card Categories & Accessories
CATEGORY_IMAGE_MAP = {
    'display-combo': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=600&auto=format&fit=crop&q=80&fm=png',
    'mobile-case-covers': 'https://images.unsplash.com/photo-1603313011101-320f26a4f6f6?w=600&auto=format&fit=crop&q=80&fm=png',
    'tempered-glass': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=600&auto=format&fit=crop&q=80&fm=png',
    'chargers-accessories': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80&fm=png',
    'speakers': 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80&fm=png',
    'combo-offers': 'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=600&auto=format&fit=crop&q=80&fm=png'
}


def load_and_seed_kaggle_data():
    cached_path = r'C:\Users\dilip\.cache\kagglehub\datasets\showmik121\smartphones-dataset-2026-1000-devices\versions\1\smartprix_smartphones_april_2026.csv'
    csv_path = None

    if os.path.exists(cached_path):
        print(f"Using local cached dataset from {cached_path}...")
        csv_path = cached_path
    else:
        try:
            print("Downloading Kaggle smartphones dataset...")
            path = kagglehub.dataset_download('showmik121/smartphones-dataset-2026-1000-devices')
            files = [f for f in os.listdir(path) if f.endswith('.csv')]
            if files:
                csv_path = os.path.join(path, files[0])
        except Exception as e:
            print(f"Kaggle download warning: {e}")

    if not csv_path or not os.path.exists(csv_path):
        print("CSV file not found")
        return

    print(f"Reading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)

    with app.app_context():
        db.create_all()
        # Ensure categories exist according to client visiting card
        card_categories_data = [
            ('Display & Combo', 'display-combo', 'Original Display Folders, AMOLED Screens & Touch Assemblies'),
            ('Mobile Case & Covers', 'mobile-case-covers', 'Premium Shockproof, Leather & Designer Phone Cases'),
            ('Tempered Glass', 'tempered-glass', '9H Hardness Glass, Matte, UV & Edge-to-Edge Protection'),
            ('Chargers & Accessories', 'chargers-accessories', 'Fast Chargers, USB Cables, Power Banks & Adapters'),
            ('Speakers', 'speakers', 'Bluetooth Speakers, Soundbars & Portable Audio Devices'),
            ('Combo Offers', 'combo-offers', 'Value Combo Packages (Screen Guard + Case + Charger Deals)'),
            ('Smartphones', 'smartphones', 'Latest 5G & Flagship Mobile Phones with Manufacturer Warranty')
        ]

        cat_objects = {}
        for name, slug, desc in card_categories_data:
            cat = Category.query.filter_by(slug=slug).first()
            if not cat:
                cat = Category(name=name, slug=slug, description=desc)
                db.session.add(cat)
                db.session.flush()
            cat_objects[slug] = cat

        smartphones_cat = cat_objects['smartphones']

        # Import smartphones from DataFrame
        added_count = 0
        existing_slugs = set(p.slug for p in Product.query.all())

        for idx, row in df.iterrows():
            model_name = str(row.get('model', '')).strip()
            if not model_name or model_name == 'nan':
                continue

            brand = str(row.get('brand_name', '')).strip().lower()
            raw_price = row.get('price', 19999)
            try:
                price = float(raw_price)
                if price <= 0 or pd.isna(price):
                    price = 19999.0
            except (ValueError, TypeError):
                price = 19999.0

            # Calculate discount price (~10% off)
            discount_price = round(price * 0.9, 0) if price > 2000 else None

            # Generate specs string
            ram = f"{int(row.get('ram', 8))}GB RAM" if pd.notna(row.get('ram')) else "8GB RAM"
            memory = f"{int(row.get('memory', 128))}GB Storage" if pd.notna(row.get('memory')) else "128GB Storage"
            battery = f"{int(row.get('battery_capacity(mAh)', 5000))}mAh Battery" if pd.notna(row.get('battery_capacity(mAh)')) else "5000mAh"
            screen = f"{row.get('screen_size', '6.67')}\" Display" if pd.notna(row.get('screen_size')) else "6.77\" AMOLED"
            processor = f"{row.get('processor_name', 'Octa-Core')}" if pd.notna(row.get('processor_name')) else "Snapdragon Octa-Core"
            has_5g = "5G Enabled" if str(row.get('has_5G', '')).lower() in ['true', '1', 'yes'] else "4G VoLTE"
            camera = f"{row.get('rear_camera', '50MP Triple Camera')}" if pd.notna(row.get('rear_camera')) else "50MP AI Camera"

            desc = f"{model_name} features {screen}, {processor}, {ram}, {memory}, {camera}, and a long-lasting {battery}. {has_5g} with official brand warranty."

            slug = re.sub(r'[^a-z0-9]+', '-', model_name.lower()).strip('-')
            if slug in existing_slugs:
                slug = f"{slug}-{idx}"
            existing_slugs.add(slug)

            img_url = BRAND_IMAGE_MAP.get(brand, BRAND_IMAGE_MAP['default'])

            spec_score = row.get('spec_score', 85)
            try:
                rating = round(min(5.0, max(4.0, float(spec_score) / 20.0)), 1)
            except (ValueError, TypeError):
                rating = 4.5

            is_featured = True if idx < 12 else False

            product = Product(
                name=model_name,
                slug=slug,
                description=desc,
                price=price,
                discount_price=discount_price,
                stock=25,
                rating=rating,
                is_featured=is_featured,
                is_active=True,
                image_url=img_url,
                category_id=smartphones_cat.id
            )
            db.session.add(product)
            added_count += 1

        # Seed Accessories corresponding to visiting card categories
        accessory_items = [
            # Display & Combo
            ('Original OLED Display & Combo Assembly (Universal)', 'display-combo', 'High-quality OEM replacement screen combo with original color saturation and touch sensitivity.', 2999, 2499, CATEGORY_IMAGE_MAP['display-combo']),
            ('Curved AMOLED Display Combo Replacement', 'display-combo', 'Premium grade curved AMOLED screen display folder combo with 120Hz refresh rate support.', 4999, 4299, CATEGORY_IMAGE_MAP['display-combo']),
            
            # Mobile Case & Covers
            ('MagSafe Transparent Hybrid Armor Case', 'mobile-case-covers', 'Ultra-clear drop-tested protective back case with built-in magnetic charging ring.', 599, 399, CATEGORY_IMAGE_MAP['mobile-case-covers']),
            ('Premium Leather Wallet Flip Cover', 'mobile-case-covers', 'Genuine feel leather flip cover with card slots, cash pocket and magnetic closure.', 799, 499, CATEGORY_IMAGE_MAP['mobile-case-covers']),
            ('Shockproof Matte Bumper Case', 'mobile-case-covers', 'Smudge-proof matte finish hard back cover with raised camera bump protection.', 499, 299, CATEGORY_IMAGE_MAP['mobile-case-covers']),

            # Tempered Glass
            ('Super HD 9H Curved UV Tempered Glass', 'tempered-glass', 'Bubble-free UV liquid adhesive glass protector with oleophobic coating against fingerprint smudges.', 399, 249, CATEGORY_IMAGE_MAP['tempered-glass']),
            ('Privacy Anti-Spy Tempered Glass Guard', 'tempered-glass', '2-way privacy screen protector preventing side peeking while maintaining touch accuracy.', 499, 349, CATEGORY_IMAGE_MAP['tempered-glass']),

            # Chargers & Accessories
            ('65W GaN Super Fast Charger Adapter', 'chargers-accessories', 'Multi-protocol GaN fast charger suitable for all modern smartphones and Type-C laptops.', 1699, 1299, CATEGORY_IMAGE_MAP['chargers-accessories']),
            ('100W Braided Type-C to Type-C Fast Cable (2m)', 'chargers-accessories', 'Heavy-duty nylon braided cable supporting 100W PD charging and high-speed data transfer.', 499, 299, CATEGORY_IMAGE_MAP['chargers-accessories']),
            ('20000mAh Digital Display Power Bank', 'chargers-accessories', 'Dual USB-A and Type-C PD 22.5W fast output power bank with real-time LED battery percentage.', 2199, 1699, CATEGORY_IMAGE_MAP['chargers-accessories']),

            # Speakers
            ('Rao SoundBlast 20W Portable Bluetooth Speaker', 'speakers', 'IPX7 waterproof wireless speaker with deep bass, dual passive radiators and 18-hour playback.', 2999, 2199, CATEGORY_IMAGE_MAP['speakers']),
            ('Mini Pocket Wireless RGB Speaker', 'speakers', 'Compact 5W speaker with dynamic multi-color RGB light show and built-in mic for clear calls.', 1299, 899, CATEGORY_IMAGE_MAP['speakers']),

            # Combo Offers
            ('Ultimate Protection Combo (Glass + Armor Case + Lens Protector)', 'combo-offers', 'Complete protection bundle featuring 9H tempered glass, armor case, and camera lens guard.', 999, 599, CATEGORY_IMAGE_MAP['combo-offers']),
            ('Super Fast Power Combo (65W Adapter + 100W Braided Cable)', 'combo-offers', 'High-power charging bundle combining 65W GaN wall plug and 2-meter braided C-to-C cable.', 1999, 1399, CATEGORY_IMAGE_MAP['combo-offers'])
        ]

        for acc_name, cat_slug, desc, price, disc_price, img in accessory_items:
            slug = re.sub(r'[^a-z0-9]+', '-', acc_name.lower()).strip('-')
            if slug not in existing_slugs:
                existing_slugs.add(slug)
                cat_id = cat_objects[cat_slug].id
                prod = Product(
                    name=acc_name,
                    slug=slug,
                    description=desc,
                    price=price,
                    discount_price=disc_price,
                    stock=50,
                    rating=4.7,
                    is_featured=True,
                    is_active=True,
                    image_url=img,
                    category_id=cat_id
                )
                db.session.add(prod)
                added_count += 1

        db.session.commit()
        print(f"Successfully seeded {added_count} products (smartphones + accessories) into database.")


if __name__ == '__main__':
    load_and_seed_kaggle_data()
