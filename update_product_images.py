"""
Updates all Kaggle-imported phones with real product-specific image URLs
sourced from GSMArena CDN and official brand image hosts.
"""
from app import app
from models import db, Product

# Real product images mapped by exact phone name (GSMArena / official CDN)
REAL_IMAGES = {
    # ─── Already in DB (original products) ────────────────────────────────────
    "Apple iPhone 15 Pro Max (256GB - Natural Titanium)": "https://fdn2.gsmarena.com/vv/pics/apple/apple-iphone-15-pro-max-1.jpg",
    "Samsung Galaxy S24 Ultra 5G (12GB RAM, 256GB)":      "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-s24-ultra-1.jpg",
    "OnePlus 12 5G (Silky Black, 16GB RAM, 512GB)":       "https://fdn2.gsmarena.com/vv/pics/oneplus/oneplus-12-1.jpg",
    "Google Pixel 8 Pro (Bay Blue, 128GB)":               "https://fdn2.gsmarena.com/vv/pics/google/google-pixel-8-pro-1.jpg",
    "Vivo V30 Pro 5G (Andaman Blue, 512GB)":              "https://fdn2.gsmarena.com/vv/pics/vivo/vivo-v30-pro-1.jpg",
    "Realme 12 Pro+ 5G (Submarine Blue, 256GB)":          "https://fdn2.gsmarena.com/vv/pics/realme/realme-12-pro-plus-5g-1.jpg",
    "Xiaomi 14 Ultra (Black Leather, 512GB)":             "https://fdn2.gsmarena.com/vv/pics/xiaomi/xiaomi-14-ultra-1.jpg",
    "Motorola Edge 50 Pro 5G (Lux Lavender, 256GB)":      "https://fdn2.gsmarena.com/vv/pics/motorola/motorola-edge-50-pro-1.jpg",

    # ─── Kaggle-imported phones ───────────────────────────────────────────────
    "OnePlus 7T Pro McLaren Edition": "https://fdn2.gsmarena.com/vv/pics/oneplus/oneplus-7t-pro-mclaren-1.jpg",
    "Realme X2 Pro":                  "https://fdn2.gsmarena.com/vv/pics/realme/realme-x2-pro-1.jpg",
    "iPhone 11 Pro Max":              "https://fdn2.gsmarena.com/vv/pics/apple/apple-iphone-11-pro-max-1.jpg",
    "iPhone 11 Pro":                  "https://fdn2.gsmarena.com/vv/pics/apple/apple-iphone-11-pro-1.jpg",
    "iPhone 11":                      "https://fdn2.gsmarena.com/vv/pics/apple/apple-iphone-11-1.jpg",
    "LG G8X ThinQ":                   "https://fdn2.gsmarena.com/vv/pics/lg/lg-g8x-thinq-1.jpg",
    "Samsung Galaxy S20 Ultra":       "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-s20-ultra-5g-1.jpg",
    "Samsung Galaxy S20+":            "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-s20-plus-1.jpg",
    "Samsung Galaxy S20":             "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-s20-1.jpg",
    "Samsung Galaxy Note 10+":        "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-note10plus-1.jpg",
    "Samsung Galaxy Note 10":         "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-note10-1.jpg",
    "Samsung Galaxy Z Flip":          "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-z-flip-1.jpg",
    "Samsung Galaxy Fold":            "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-fold-1.jpg",
    "Huawei Mate 30 Pro":             "https://fdn2.gsmarena.com/vv/pics/huawei/huawei-mate-30-pro-1.jpg",
    "Huawei P30 Pro":                 "https://fdn2.gsmarena.com/vv/pics/huawei/huawei-p30-pro-1.jpg",
    "Huawei P30":                     "https://fdn2.gsmarena.com/vv/pics/huawei/huawei-p30-1.jpg",
    "Google Pixel 4 XL":              "https://fdn2.gsmarena.com/vv/pics/google/google-pixel-4-xl-1.jpg",
    "Google Pixel 4":                 "https://fdn2.gsmarena.com/vv/pics/google/google-pixel-4-1.jpg",
    "HP Elite x3":                    "https://fdn2.gsmarena.com/vv/pics/hp/hp-elite-x3-1.jpg",
    "HTC U12+":                       "https://fdn2.gsmarena.com/vv/pics/htc/htc-u12-plus-1.jpg",
    "Sony Xperia XA2 Ultra":          "https://fdn2.gsmarena.com/vv/pics/sony/sony-xperia-xa2-ultra-1.jpg",
    "Sony Xperia 1":                  "https://fdn2.gsmarena.com/vv/pics/sony/sony-xperia-1-1.jpg",
    "Nokia 9 PureView":               "https://fdn2.gsmarena.com/vv/pics/nokia/nokia-9-pureview-1.jpg",
    "OnePlus 7 Pro":                  "https://fdn2.gsmarena.com/vv/pics/oneplus/oneplus-7-pro-1.jpg",
    "OnePlus 7T":                     "https://fdn2.gsmarena.com/vv/pics/oneplus/oneplus-7t-1.jpg",
    "Realme XT":                      "https://fdn2.gsmarena.com/vv/pics/realme/realme-xt-1.jpg",
    "Realme X":                       "https://fdn2.gsmarena.com/vv/pics/realme/realme-x-1.jpg",
    "Realme 5 Pro":                   "https://fdn2.gsmarena.com/vv/pics/realme/realme-5-pro-1.jpg",
    "Vivo V17 Pro":                   "https://fdn2.gsmarena.com/vv/pics/vivo/vivo-v17-pro-1.jpg",
    "Vivo S1 Pro":                    "https://fdn2.gsmarena.com/vv/pics/vivo/vivo-s1-pro-1.jpg",
    "Motorola One Action":            "https://fdn2.gsmarena.com/vv/pics/motorola/motorola-one-action-1.jpg",
    "Motorola Moto G8 Plus":          "https://fdn2.gsmarena.com/vv/pics/motorola/motorola-moto-g8-plus-1.jpg",
    "Xiaomi Mi Note 10":              "https://fdn2.gsmarena.com/vv/pics/xiaomi/xiaomi-mi-note-10-1.jpg",
    "Xiaomi Redmi Note 8 Pro":        "https://fdn2.gsmarena.com/vv/pics/xiaomi/xiaomi-redmi-note-8-pro-1.jpg",
    "Xiaomi Mi 9T Pro":               "https://fdn2.gsmarena.com/vv/pics/xiaomi/xiaomi-mi-9t-pro-1.jpg",
    "Oppo Reno 2":                    "https://fdn2.gsmarena.com/vv/pics/oppo/oppo-reno2-1.jpg",
    "Oppo Reno":                      "https://fdn2.gsmarena.com/vv/pics/oppo/oppo-reno-1.jpg",
    "Samsung Galaxy A70":             "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-a70-1.jpg",
    "Samsung Galaxy A50":             "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-a50-1.jpg",
    "Samsung Galaxy M30s":            "https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-m30s-1.jpg",
    "Redmi Note 8":                   "https://fdn2.gsmarena.com/vv/pics/xiaomi/xiaomi-redmi-note-8-1.jpg",
    "Realme 5s":                      "https://fdn2.gsmarena.com/vv/pics/realme/realme-5s-1.jpg",
    "Vivo Z1 Pro":                    "https://fdn2.gsmarena.com/vv/pics/vivo/vivo-z1-pro-1.jpg",
    "Asus 6Z":                        "https://fdn2.gsmarena.com/vv/pics/asus/asus-6z-1.jpg",
}

with app.app_context():
    updated = 0
    not_found = 0
    all_phones = Product.query.filter_by(is_active=True).all()

    for product in all_phones:
        if product.name in REAL_IMAGES:
            product.image_url = REAL_IMAGES[product.name]
            updated += 1
        else:
            not_found += 1

    db.session.commit()
    print(f"Updated: {updated} products with real GSMArena images")
    print(f"No mapping found: {not_found} products (kept existing image)")
