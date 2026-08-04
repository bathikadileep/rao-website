import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, User, Category, Product, Service


from clean_catalog import clean_and_seed_real_products


def seed():
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        if not User.query.filter_by(email='admin@rao.com').first():
            admin = User(
                email='admin@rao.com',
                username='admin',
                full_name='Rao Admin',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print('Created admin user: admin@rao.com / admin123')

        # Create demo user
        if not User.query.filter_by(email='demo@rao.com').first():
            demo = User(
                email='demo@rao.com',
                username='demo',
                full_name='Demo Customer'
            )
            demo.set_password('demo123')
            db.session.add(demo)
            print('Created demo user: demo@rao.com / demo123')

        db.session.commit()

        # Seed services matching client visiting card
        if Service.query.count() == 0:
            services_data = [
                ('Display & Combo Replacement', 'Cracked or broken phone screen replacement with original OEM display folders & touch glass. Instant installation.', 2499, '1-2 hours', 'fa-mobile-screen'),
                ('Mobile Repairing (Chip & Hardware Level)', 'Complete motherboard, IC, micro-soldering, and hardware repair by certified mobile technicians.', 1499, '1-3 hours', 'fa-toolbox'),
                ('Tempered Glass & Curved Screen Fitting', '9H hardness UV liquid, anti-peeking privacy, and curved glass installation with zero air bubbles.', 299, '15 min', 'fa-shield-halved'),
                ('Battery & Fast Charge Repair', 'Original high-capacity battery replacement and quick charging solution for iPhone, Samsung, OnePlus & all brands.', 1299, '30 min', 'fa-battery-full'),
                ('Water & Liquid Damage Treatment', 'Emergency ultrasonic chemical bath cleaning and dehydration for water dropped smartphones.', 1999, '2-4 hours', 'fa-droplet'),
                ('Speaker, Mic & Receiver Repair', 'Fix muffled voices, silent ear-receivers, broken ringers, and distorted speakers.', 799, '30 min', 'fa-volume-high'),
            ]

            for name, desc, price, time, icon in services_data:
                service = Service(
                    name=name,
                    slug=name.lower().replace(' & ', '-').replace(' ', '-').replace('&', 'and').replace('(', '').replace(')', ''),
                    description=desc,
                    price=price,
                    estimated_time=time,
                    image_icon=icon,
                    is_active=True,
                )
                db.session.add(service)

            db.session.commit()
            print(f'Seeded {len(services_data)} client visiting card repair services')

        if Product.query.count() == 0:
            clean_and_seed_real_products()


if __name__ == '__main__':
    seed()
