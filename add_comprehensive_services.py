import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from app import app
from models import db, Service

SERVICES = [
    {
        'name': 'Display & Combo Replacement',
        'slug': 'display-combo-replacement',
        'description': 'Original OEM AMOLED, OLED & IPS folder screen replacement. Includes touch screen glass replacement and instant 1-hour installation.',
        'price': 1999,
        'estimated_time': '45 - 60 min',
        'image_icon': 'fa-mobile-screen'
    },
    {
        'name': 'Mobile Repairing (Chip Level & Motherboard)',
        'slug': 'mobile-repairing-chip-level',
        'description': 'Advanced IC replacement, micro-soldering, short-circuit fixing, and hardware diagnosis by certified master technicians.',
        'price': 1499,
        'estimated_time': '1 - 3 hours',
        'image_icon': 'fa-microchip'
    },
    {
        'name': 'Tempered Glass & Curved Screen Guard Fitting',
        'slug': 'tempered-glass-fitting',
        'description': 'Professional installation of 9H hardness UV liquid glue glass, matte anti-fingerprint, and 11D curved edge-to-edge guards with zero bubbles.',
        'price': 199,
        'estimated_time': '15 min',
        'image_icon': 'fa-shield-halved'
    },
    {
        'name': 'Battery Replacement & Health Restore',
        'slug': 'battery-replacement',
        'description': 'Original high-capacity replacement batteries with 100% health restore, fast charge compatibility, and 6-month warranty.',
        'price': 999,
        'estimated_time': '30 min',
        'image_icon': 'fa-battery-full'
    },
    {
        'name': 'Water & Liquid Damage Recovery',
        'slug': 'water-damage-repair',
        'description': 'Emergency ultrasonic chemical bath cleaning, board drying, and corrosion cleanup for liquid-exposed smartphones.',
        'price': 1299,
        'estimated_time': '2 - 4 hours',
        'image_icon': 'fa-droplet'
    },
    {
        'name': 'Speaker, Mic & Earpiece Repair',
        'slug': 'speaker-mic-repair',
        'description': 'Fix distorted audio, low ringer volume, faulty microphones, and silent earpiece receivers using original acoustic parts.',
        'price': 599,
        'estimated_time': '30 min',
        'image_icon': 'fa-volume-high'
    },
    {
        'name': 'Charging Port & Type-C Jack Repair',
        'slug': 'charging-port-repair',
        'description': 'Fix loose charging connections, slow charging issues, damaged Type-C / Lightning ports with original connector replacements.',
        'price': 499,
        'estimated_time': '30 min',
        'image_icon': 'fa-plug-circle-bolt'
    },
    {
        'name': 'Camera Module & Glass Lens Replacement',
        'slug': 'camera-repair',
        'description': 'Fix blurry focus, cracked camera glass lens, OIS jitter, or non-working front and rear camera sensors.',
        'price': 1199,
        'estimated_time': '45 min',
        'image_icon': 'fa-camera'
    },
    {
        'name': 'Software Flash, OS Update & Boot Loop Fix',
        'slug': 'software-os-flash',
        'description': 'Unbrick frozen phones, fix infinite restart loops, install official stock OS updates, and resolve system crashes.',
        'price': 499,
        'estimated_time': '45 min',
        'image_icon': 'fa-code'
    },
    {
        'name': 'Back Glass & Phone Body Housing Replacement',
        'slug': 'back-glass-housing-replacement',
        'description': 'Laser back glass removal and premium aluminum/glass back cover housing replacement for iPhone & flagship phones.',
        'price': 1799,
        'estimated_time': '1 - 2 hours',
        'image_icon': 'fa-mobile-retro'
    }
]


def add_services():
    with app.app_context():
        db.create_all()
        added = 0
        updated = 0
        for item in SERVICES:
            svc = Service.query.filter_by(slug=item['slug']).first()
            if not svc:
                svc = Service(
                    name=item['name'],
                    slug=item['slug'],
                    description=item['description'],
                    price=item['price'],
                    estimated_time=item['estimated_time'],
                    image_icon=item['image_icon'],
                    is_active=True
                )
                db.session.add(svc)
                added += 1
            else:
                svc.name = item['name']
                svc.description = item['description']
                svc.price = item['price']
                svc.estimated_time = item['estimated_time']
                svc.image_icon = item['image_icon']
                svc.is_active = True
                updated += 1
        db.session.commit()
        print(f"Services database updated: {added} new services added, {updated} existing services refreshed.")


if __name__ == '__main__':
    add_services()
