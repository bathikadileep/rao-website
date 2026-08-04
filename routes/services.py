from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Service, ServiceBooking

services_bp = Blueprint('services', __name__)

TIME_SLOTS = [
    '10:00 AM', '11:00 AM', '12:00 PM', '01:00 PM',
    '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM',
    '06:00 PM', '07:00 PM'
]


@services_bp.route('/services')
def services():
    all_services = Service.query.filter_by(is_active=True).all()
    return render_template('services/services.html', services=all_services)


@services_bp.route('/services/<slug>')
def service_detail(slug):
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template('services/service_detail.html', service=service, time_slots=TIME_SLOTS)


@services_bp.route('/services/<slug>/book', methods=['GET', 'POST'])
@login_required
def book_service(slug):
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()

    if request.method == 'POST':
        phone_model = request.form.get('phone_model', '').strip()
        booking_date = request.form.get('booking_date', '')
        time_slot = request.form.get('time_slot', '')
        notes = request.form.get('notes', '').strip()

        if not phone_model or not booking_date or not time_slot:
            flash('Please fill in all required fields.', 'error')
            return render_template('services/book_service.html', service=service, time_slots=TIME_SLOTS, today=date.today().isoformat())

        try:
            booking_dt = datetime.strptime(booking_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date selected.', 'error')
            return render_template('services/book_service.html', service=service, time_slots=TIME_SLOTS, today=date.today().isoformat())

        if booking_dt < date.today():
            flash('Please select a future date.', 'error')
            return render_template('services/book_service.html', service=service, time_slots=TIME_SLOTS, today=date.today().isoformat())

        booking = ServiceBooking(
            user_id=current_user.id,
            service_id=service.id,
            phone_model=phone_model,
            booking_date=booking_dt,
            time_slot=time_slot,
            notes=notes,
            status='pending'
        )
        db.session.add(booking)
        db.session.commit()

        flash('Service booked successfully! We will confirm your appointment soon.', 'success')
        return redirect(url_for('services.booking_confirmation', booking_id=booking.id))

    return render_template('services/book_service.html', service=service, time_slots=TIME_SLOTS, today=date.today().isoformat())


@services_bp.route('/services/booking/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    booking = ServiceBooking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()
    return render_template('services/booking_confirmation.html', booking=booking)


@services_bp.route('/services/<slug>/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = ServiceBooking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()
    if booking.status in ('pending', 'confirmed'):
        booking.status = 'cancelled'
        db.session.commit()
        flash('Service booking cancelled.', 'success')
    else:
        flash('This booking cannot be cancelled.', 'error')
    return redirect(url_for('dashboard.dashboard'))
