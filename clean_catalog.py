import re
from sqlalchemy import text
from app import app
from models import db, Category, Product

# REAL AUTHENTIC PRODUCTS ONLY
REAL_PRODUCTS = [
    # --- Smartphones ---
    {
        "name": "Apple iPhone 15 Pro Max (256GB - Natural Titanium)",
        "cat_slug": "smartphones",
        "desc": "A17 Pro chip, Titanium design with textured matte glass back, Action button, and 48MP Main camera with 5x Telephoto.",
        "price": 159900,
        "discount_price": 148900,
        "rating": 4.9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Samsung Galaxy S24 Ultra 5G (12GB RAM, 256GB)",
        "cat_slug": "smartphones",
        "desc": "Snapdragon 8 Gen 3 for Galaxy, Built-in S Pen, 200MP Quad Telephoto Camera, Titanium frame and Galaxy AI features.",
        "price": 129999,
        "discount_price": 119999,
        "rating": 4.9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "OnePlus 12 5G (Silky Black, 16GB RAM, 512GB)",
        "cat_slug": "smartphones",
        "desc": "Snapdragon 8 Gen 3, 4th Gen Hasselblad Camera System for Mobile, 2K 120Hz ProXDR Display with 5400 mAh battery & 100W SUPERVOOC.",
        "price": 69999,
        "discount_price": 64999,
        "rating": 4.8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Google Pixel 8 Pro (Bay Blue, 128GB)",
        "cat_slug": "smartphones",
        "desc": "Google Tensor G3 chip, fully upgraded camera system with 5x telephoto, Super Actua display, and 7 years of OS updates.",
        "price": 106999,
        "discount_price": 93999,
        "rating": 4.7,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Vivo V30 Pro 5G (Andaman Blue, 512GB)",
        "cat_slug": "smartphones",
        "desc": "ZEISS Style Portrait, 50MP Sony IMX920 Main Camera, 3D Curved AMOLED Display, and MediaTek Dimensity 8200.",
        "price": 46999,
        "discount_price": 41999,
        "rating": 4.7,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Realme 12 Pro+ 5G (Submarine Blue, 256GB)",
        "cat_slug": "smartphones",
        "desc": "64MP Periscope Portrait Camera with 120X SuperZoom, Luxury Watch Design, Snapdragon 7s Gen 2 and 120Hz Curved Display.",
        "price": 34999,
        "discount_price": 29999,
        "rating": 4.6,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1546054454-aa26e2b734c7?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Xiaomi 14 Ultra (Black Leather, 512GB)",
        "cat_slug": "smartphones",
        "desc": "Leica Quad Camera System with 1-inch sensor, Stepless variable aperture, Snapdragon 8 Gen 3 and WQHD+ AMOLED display.",
        "price": 99999,
        "discount_price": 89999,
        "rating": 4.8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Motorola Edge 50 Pro 5G (Lux Lavender, 256GB)",
        "cat_slug": "smartphones",
        "desc": "World's 1st Pantone Validated Camera & Display, 125W TurboPower charging, 50MP AI powered camera and IP68 underwater protection.",
        "price": 36999,
        "discount_price": 31999,
        "rating": 4.6,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&auto=format&fit=crop&q=80"
    },

    # --- Display & Combo ---
    {
        "name": "Original OLED Display & Combo Assembly (Universal)",
        "cat_slug": "display-combo",
        "desc": "High-quality OEM replacement screen combo with original color saturation and touch sensitivity.",
        "price": 2999,
        "discount_price": 2499,
        "rating": 4.8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Curved AMOLED Display Combo Replacement",
        "cat_slug": "display-combo",
        "desc": "Premium grade curved AMOLED screen display folder combo with 120Hz refresh rate support.",
        "price": 4999,
        "discount_price": 4299,
        "rating": 4.9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&auto=format&fit=crop&q=80"
    },

    # --- Mobile Case & Covers ---
    {
        "name": "MagSafe Transparent Hybrid Armor Case",
        "cat_slug": "mobile-case-covers",
        "desc": "Ultra-clear drop-tested protective back case with built-in magnetic charging ring.",
        "price": 599,
        "discount_price": 399,
        "rating": 4.7,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1603313011101-320f26a4f6f6?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Premium Leather Wallet Flip Cover",
        "cat_slug": "mobile-case-covers",
        "desc": "Genuine feel leather flip cover with card slots, cash pocket and magnetic closure.",
        "price": 799,
        "discount_price": 499,
        "rating": 4.8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1541877944-ac82a091518a?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Shockproof Matte Bumper Case",
        "cat_slug": "mobile-case-covers",
        "desc": "Smudge-proof matte finish hard back cover with raised camera bump protection.",
        "price": 499,
        "discount_price": 299,
        "rating": 4.7,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop&q=80"
    },

    # --- Tempered Glass ---
    {
        "name": "Super HD 9H Curved UV Tempered Glass",
        "cat_slug": "tempered-glass",
        "desc": "Bubble-free UV liquid adhesive glass protector with oleophobic coating against fingerprint smudges.",
        "price": 399,
        "discount_price": 249,
        "rating": 4.8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Privacy Anti-Spy Tempered Glass Guard",
        "cat_slug": "tempered-glass",
        "desc": "2-way privacy screen protector preventing side peeking while maintaining touch accuracy.",
        "price": 499,
        "discount_price": 349,
        "rating": 4.9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop&q=80"
    },

    # --- Chargers & Accessories ---
    {
        "name": "65W GaN Super Fast Charger Adapter",
        "cat_slug": "chargers-accessories",
        "desc": "Multi-protocol GaN fast charger suitable for all modern smartphones and Type-C laptops.",
        "price": 1699,
        "discount_price": 1299,
        "rating": 4.9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "100W Braided Type-C to Type-C Fast Cable (2m)",
        "cat_slug": "chargers-accessories",
        "desc": "Heavy-duty nylon braided cable supporting 100W PD charging and high-speed data transfer.",
        "price": 499,
        "discount_price": 299,
        "rating": 4.8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "20000mAh Digital Display Power Bank",
        "cat_slug": "chargers-accessories",
        "desc": "Dual USB-A and Type-C PD 22.5W fast output power bank with real-time LED battery percentage.",
        "price": 2199,
        "discount_price": 1699,
        "rating": 4.9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1609592424074-123497d3910c?w=600&auto=format&fit=crop&q=80"
    },

    # --- Speakers ---
    {
        "name": "Rao SoundBlast 20W Portable Bluetooth Speaker",
        "cat_slug": "speakers",
        "desc": "IPX7 waterproof wireless speaker with deep bass, dual passive radiators and 18-hour playback.",
        "price": 2999,
        "discount_price": 2199,
        "rating": 4.8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Mini Pocket Wireless RGB Speaker",
        "cat_slug": "speakers",
        "desc": "Compact 5W speaker with dynamic multi-color RGB light show and built-in mic for clear calls.",
        "price": 1299,
        "discount_price": 899,
        "rating": 4.6,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&auto=format&fit=crop&q=80"
    },

    # --- Combo Offers ---
    {
        "name": "Ultimate Protection Combo (Glass + Armor Case + Lens Protector)",
        "cat_slug": "combo-offers",
        "desc": "Complete protection bundle featuring 9H tempered glass, armor case, and camera lens guard.",
        "price": 999,
        "discount_price": 599,
        "rating": 4.9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=600&auto=format&fit=crop&q=80"
    },
    {
        "name": "Super Fast Power Combo (65W Adapter + 100W Braided Cable)",
        "cat_slug": "combo-offers",
        "desc": "High-power charging bundle combining 65W GaN wall plug and 2-meter braided C-to-C cable.",
        "price": 1999,
        "discount_price": 1399,
        "rating": 4.9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80"
    }
]

def clean_and_seed_real_products():
    with app.app_context():
        # Truncate products and dependent tables cleanly
        db.session.execute(text("TRUNCATE TABLE order_items, orders, cart_items, products RESTART IDENTITY CASCADE;"))
        db.session.commit()
        print("Cleanly purged fake AI products and test order data.")

        # Get category mapping
        categories = {c.slug: c.id for c in Category.query.all()}

        # Insert real curated products
        added = 0
        existing_slugs = set()
        for item in REAL_PRODUCTS:
            base_slug = re.sub(r'[^a-z0-9]+', '-', item['name'].lower()).strip('-')
            slug = base_slug
            idx = 1
            while slug in existing_slugs:
                slug = f"{base_slug}-{idx}"
                idx += 1
            existing_slugs.add(slug)

            cat_id = categories.get(item['cat_slug'])
            if cat_id:
                p = Product(
                    name=item['name'],
                    slug=slug,
                    description=item['desc'],
                    price=item['price'],
                    discount_price=item['discount_price'],
                    stock=30,
                    rating=item['rating'],
                    is_featured=item['is_featured'],
                    is_active=True,
                    image_url=item['image_url'],
                    category_id=cat_id
                )
                db.session.add(p)
                added += 1

        db.session.commit()
        print(f"Successfully added {added} authentic real products with HD images!")

if __name__ == '__main__':
    clean_and_seed_real_products()
