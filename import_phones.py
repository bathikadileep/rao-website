import json
from app import app
from models import db, Product, Category

PRODUCTS = [
    {"title":"iPhone 5s","description":"The iPhone 5s is a classic smartphone known for its compact design and advanced features during its release. While it's an older model, it still provides a reliable user experience.","price":199.99,"discountPercentage":12.91,"rating":2.83,"stock":25,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/iphone-5s/thumbnail.webp"},
    {"title":"iPhone 6","description":"The iPhone 6 is a stylish and capable smartphone with a larger display and improved performance. It introduced new features and design elements, making it a popular choice in its time.","price":299.99,"discountPercentage":6.69,"rating":3.41,"stock":60,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/iphone-6/thumbnail.webp"},
    {"title":"iPhone 13 Pro","description":"The iPhone 13 Pro is a cutting-edge smartphone with a powerful camera system, high-performance chip, and stunning display. It offers advanced features for users who demand top-notch technology.","price":1099.99,"discountPercentage":9.37,"rating":4.12,"stock":56,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/iphone-13-pro/thumbnail.webp"},
    {"title":"iPhone X","description":"The iPhone X is a flagship smartphone featuring a bezel-less OLED display, facial recognition technology (Face ID), and impressive performance. It represents a milestone in iPhone design and innovation.","price":899.99,"discountPercentage":19.59,"rating":2.51,"stock":37,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/iphone-x/thumbnail.webp"},
    {"title":"Oppo A57","description":"The Oppo A57 is a mid-range smartphone known for its sleek design and capable features. It offers a balance of performance and affordability, making it a popular choice.","price":249.99,"discountPercentage":2.43,"rating":3.94,"stock":19,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/oppo-a57/thumbnail.webp"},
    {"title":"Oppo F19 Pro Plus","description":"The Oppo F19 Pro Plus is a feature-rich smartphone with a focus on camera capabilities. It boasts advanced photography features and a powerful performance for a premium user experience.","price":399.99,"discountPercentage":18.64,"rating":3.51,"stock":78,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/oppo-f19-pro-plus/thumbnail.webp"},
    {"title":"Oppo K1","description":"The Oppo K1 series offers a range of smartphones with various features and specifications. Known for their stylish design and reliable performance, the Oppo K1 series caters to diverse user preferences.","price":299.99,"discountPercentage":18.29,"rating":4.25,"stock":55,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/oppo-k1/thumbnail.webp"},
    {"title":"Realme C35","description":"The Realme C35 is a budget-friendly smartphone with a focus on providing essential features for everyday use. It offers a reliable performance and user-friendly experience.","price":149.99,"discountPercentage":15.3,"rating":4.2,"stock":48,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/realme-c35/thumbnail.webp"},
    {"title":"Realme X","description":"The Realme X is a mid-range smartphone known for its sleek design and impressive display. It offers a good balance of performance and camera capabilities for users seeking a quality device.","price":299.99,"discountPercentage":6.95,"rating":3.7,"stock":12,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/realme-x/thumbnail.webp"},
    {"title":"Realme XT","description":"The Realme XT is a feature-rich smartphone with a focus on camera technology. It comes equipped with advanced camera sensors, delivering high-quality photos and videos for photography enthusiasts.","price":349.99,"discountPercentage":11.51,"rating":4.58,"stock":80,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/realme-xt/thumbnail.webp"},
    {"title":"Samsung Galaxy S7","description":"The Samsung Galaxy S7 is a flagship smartphone known for its sleek design and advanced features. It features a high-resolution display, powerful camera, and robust performance.","price":299.99,"discountPercentage":19.55,"rating":3.3,"stock":67,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s7/thumbnail.webp"},
    {"title":"Samsung Galaxy S8","description":"The Samsung Galaxy S8 is a premium smartphone with an Infinity Display, offering a stunning visual experience. It boasts advanced camera capabilities and cutting-edge technology.","price":499.99,"discountPercentage":19.45,"rating":4.4,"stock":0,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s8/thumbnail.webp"},
    {"title":"Samsung Galaxy S10","description":"The Samsung Galaxy S10 is a flagship device featuring a dynamic AMOLED display, versatile camera system, and powerful performance. It represents innovation and excellence in smartphone technology.","price":699.99,"discountPercentage":5.59,"rating":3.06,"stock":19,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s10/thumbnail.webp"},
    {"title":"Vivo S1","description":"The Vivo S1 is a stylish and mid-range smartphone offering a blend of design and performance. It features a vibrant display, capable camera system, and reliable functionality.","price":249.99,"discountPercentage":10.17,"rating":3.5,"stock":50,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/vivo-s1/thumbnail.webp"},
    {"title":"Vivo V9","description":"The Vivo V9 is a smartphone known for its sleek design and emphasis on capturing high-quality selfies. It features a notch display, dual-camera setup, and a modern design.","price":299.99,"discountPercentage":17.67,"rating":3.6,"stock":82,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/vivo-v9/thumbnail.webp"},
    {"title":"Vivo X21","description":"The Vivo X21 is a premium smartphone with a focus on cutting-edge technology. It features an in-display fingerprint sensor, a high-resolution display, and advanced camera capabilities.","price":499.99,"discountPercentage":17.41,"rating":4.26,"stock":7,"thumbnail":"https://cdn.dummyjson.com/product-images/smartphones/vivo-x21/thumbnail.webp"},
]

INR_RATE = 83

with app.app_context():
    cat = Category.query.filter_by(slug='smartphones').first()
    if not cat:
        cat = Category(name='Smartphones', slug='smartphones', description='Latest smartphones')
        db.session.add(cat)
        db.session.commit()

    added = 0
    skipped = 0

    for p in PRODUCTS:
        name = p['title']
        if Product.query.filter_by(name=name).first():
            skipped += 1
            print('SKIP: ' + name)
            continue

        price_inr = round(p['price'] * INR_RATE)
        disc = p.get('discountPercentage', 0)
        discount_inr = round(price_inr * (1 - disc/100)) if disc > 0 else None

        slug = name.lower().replace(' ', '-').replace('(','').replace(')','').replace('.','').replace('/','')
        base = slug
        n = 1
        while Product.query.filter_by(slug=slug).first():
            slug = base + '-' + str(n)
            n += 1

        product = Product(
            name=name, slug=slug,
            description=p.get('description',''),
            price=price_inr,
            discount_price=discount_inr,
            image_url=p.get('thumbnail',''),
            stock=max(p.get('stock', 0), 0),
            rating=round(p.get('rating', 4.0), 1),
            category_id=cat.id,
            is_featured=(p.get('rating', 0) >= 4.0),
            is_active=True,
        )
        db.session.add(product)
        added += 1
        print('+ ' + name + ' | Rs.' + str(price_inr) + ' | Rating:' + str(p.get('rating')))

    db.session.commit()
    print('')
    print('DONE! Added=' + str(added) + ' | Skipped=' + str(skipped))
