"""This module defines user's routes for the application"""
import os
import re
from functools import wraps
from datetime import datetime
import googlemaps
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, render_template, redirect, url_for, flash, request,abort
from flask_login import login_required, current_user
from app.models import Car, Booking,User
from app.email_templates import send_booking_confirmation,send_booking_modification_email,send_booking_cancellation_email
from app.utils import get_secret
from app import db

# Get the secret
# secret_name = "23410698_gmaps_api_key"
# region_name = "eu-west-1"
# secret_data = get_secret(secret_name, region_name)
# print(secret_data)
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
print("google_maps_api_key",google_maps_api_key)
# google_maps_api_key = secret_data['GOOGLE_MAPS_API_KEY']

gmaps = googlemaps.Client(key=google_maps_api_key)

user = Blueprint('user', __name__)

# Constants for fare calculation
BASE_FARE = 3
DISTANCE_RATE = 2  # € per km
TIME_RATE = 0.5    # € per minute


def user_required(f):
    """
    Custom decorator to check if user is a regular user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.get_id().startswith('user_'):
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('auth.user_login'))
        return f(*args, **kwargs)
    return decorated_function


@user.route('/user_profile', methods=['GET', 'POST'])
@login_required
@user_required
def user_profile():
    """
    This function lets user edit their personal information
    """
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('user.user_profile'))

        if username != current_user.username and User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('user.user_profile'))

        # Update basic information
        current_user.name = name
        current_user.email = email
        current_user.phone = phone
        current_user.username = username

        # If user wants to change password
        if new_password:
            # Verify current password
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('user.user_profile'))

            # Validate new password
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return redirect(url_for('user.profile'))

            # Password validation
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long', 'danger')
                return redirect(url_for('user.user_profile'))

            if not re.search(r'\d', new_password):
                flash('Password must contain at least one number', 'danger')
                return redirect(url_for('user.user_profile'))

            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                flash('Password must contain at least one special character', 'danger')
                return redirect(url_for('user.user_profile'))

            # Set new password
            current_user.set_password(new_password)

        try:
            db.session.commit()
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('user.user_profile'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('user/user_profile.html')

@user.route('/dashboard')
@login_required
@user_required
def dashboard():
    """
    This function displays user dashboard
    """
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_time.desc()).all()
    return render_template('user/user_dashboard.html', bookings=bookings)

@user.route('/book_cab', methods=['GET', 'POST'])
@login_required
@user_required
def book_cab():
    """
    This function defines user's cab booking
    """
    if request.method == 'POST':
        # Get form data
        pickup_lat = request.form.get('pickup_lat')
        pickup_lng = request.form.get('pickup_lng')
        pickup_address = request.form.get('pickup_address')

        dropoff_lat = request.form.get('dropoff_lat')
        dropoff_lng = request.form.get('dropoff_lng')
        dropoff_address = request.form.get('dropoff_address')

        date_str = request.form.get('date')
        time_str = request.form.get('time')
        car_id = request.form.get('car_type')

        # Validate input
        if not all([pickup_lat, pickup_lng, pickup_address,
                   dropoff_lat, dropoff_lng, dropoff_address,
                   date_str, time_str, car_id]):
            flash('All fields are required', 'danger')
            return redirect(url_for('user.book_cab'))

        # Convert date and time strings to datetime object
        try:
            booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return redirect(url_for('user.book_cab'))

        try:
            pickup_coords = f"{pickup_lat},{pickup_lng}"
            dropoff_coords = f"{dropoff_lat},{dropoff_lng}"

            result = gmaps.distance_matrix(
                origins=pickup_coords,
                destinations=dropoff_coords,
                mode="driving",
                units="metric"
            )
            if result['rows'][0]['elements'][0]['status'] != "OK":
                abort(400, description="Unable to calculate distance")
        except Exception as e:
            flash(f'Error calculating distance: {str(e)}', 'danger')
            abort(400, description=f"Error calculating distance: {str(e)}")

        car = Car.query.get(car_id)
        if not car:
            flash('Selected car not available', 'danger')
            return redirect(url_for('user.book_cab'))

        distance_value = result['rows'][0]['elements'][0]['distance']['value']  # in meters
        duration_value = result['rows'][0]['elements'][0]['duration']['value']  # in seconds
        # Calculate fare
        distance_km = distance_value / 1000
        duration_min = duration_value / 60
        fare = BASE_FARE + (distance_km * car.rate_per_km) + (duration_min * TIME_RATE)
        # Create new booking
        new_booking = Booking(
            user_id=current_user.id,
            car_id=car_id,
            pickup_latitude=pickup_lat,
            pickup_longitude=pickup_lng,
            pickup_address=pickup_address,
            dropoff_latitude=dropoff_lat,
            dropoff_longitude=dropoff_lng,
            dropoff_address=dropoff_address,
            booking_time=datetime.utcnow(),  # When the user made the booking
            journey_date=booking_datetime,   # When the ride is scheduled
            status='confirmed',              # Changed from 'pending' to 'confirmed'
            estimated_fare=fare
        )

        try:
            db.session.add(new_booking)
            db.session.commit()

            email_sent = send_booking_confirmation(current_user, new_booking, car, fare)
            if email_sent:
                flash('Booking successful! A confirmation email has been sent to your email address.', 'success')
            else:
                flash('Booking successful! However, we could not send the confirmation email.', 'warning')

            return redirect(url_for('user.dashboard'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('user.book_cab'))

    # GET request - show booking form
    cars = Car.query.filter_by(is_available=True).all()
    return render_template('user/book_cab.html', cars=cars,google_maps_api_key=google_maps_api_key)

@user.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
@user_required
def cancel_booking(booking_id):
    """
    This function lets user cancel their booking
    """
    booking = Booking.query.get_or_404(booking_id)

    # Check if booking belongs to current user
    if booking.user_id != current_user.id:
        flash('You do not have permission to cancel this booking', 'danger')
        return redirect(url_for('user.dashboard'))

    # Check if booking is confirmed or modified (both can be cancelled)
    if booking.status not in ['confirmed', 'modified']:
        flash('Only confirmed or modified bookings can be cancelled', 'danger')
        return redirect(url_for('user.dashboard'))

    try:
        # Update booking status
        booking.status = 'cancelled'

        # Make car available again
        car = Car.query.get(booking.car_id)
        car.is_available = True

        db.session.commit()
        email_sent = send_booking_cancellation_email(
                current_user,
                booking
            )

        if email_sent:
            flash('Booking cancelled successfully! A cancellation email has been sent to your email address.', 'success')
        else:
            flash('Booking cancelled successfully! However, we could not send the cancellation email.', 'warning')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error cancelling booking: {str(e)}', 'danger')

    return redirect(url_for('user.dashboard'))


@user.route('/modify_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@user_required
def modify_booking(booking_id):
    """
    This function lets user modify their bookings
    """
    booking = Booking.query.get_or_404(booking_id)
    # Check if booking belongs to current user
    if booking.user_id != current_user.id:
        flash('You do not have permission to modify this booking', 'danger')
        return redirect(url_for('user.dashboard'))

    # Check if booking is confirmed (only confirmed bookings can be modified)
    if booking.status != 'confirmed':  # Changed from 'pending' to 'confirmed'
        flash('Only confirmed bookings can be modified', 'danger')
        return redirect(url_for('user.dashboard'))

    # Get available cars for selection
    cars = Car.query.filter_by(is_available=True).all()
    # Include the currently assigned car even if not available
    if booking.vehicle not in cars:
        cars.append(booking.vehicle)

    if request.method == 'POST':
        # Get form data
        pickup_lat = request.form.get('pickup_lat')
        pickup_lng = request.form.get('pickup_lng')
        pickup_address = request.form.get('pickup_address')

        dropoff_lat = request.form.get('dropoff_lat')
        dropoff_lng = request.form.get('dropoff_lng')
        dropoff_address = request.form.get('dropoff_address')

        date_str = request.form.get('date')
        time_str = request.form.get('time')
        car_id = request.form.get('car_type')

        # Validate input
        if not all([pickup_lat, pickup_lng, pickup_address,
                   dropoff_lat, dropoff_lng, dropoff_address,
                   date_str, time_str, car_id]):
            flash('All fields are required', 'danger')
            return redirect(url_for('user.modify_booking', booking_id=booking_id))

        # Convert date and time strings to datetime object
        try:
            booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return redirect(url_for('user.modify_booking', booking_id=booking_id))

        try:
            pickup_coords = f"{pickup_lat},{pickup_lng}"
            dropoff_coords = f"{dropoff_lat},{dropoff_lng}"

            result = gmaps.distance_matrix(
                origins=pickup_coords,
                destinations=dropoff_coords,
                mode="driving",
                units="metric"
            )
            if result['rows'][0]['elements'][0]['status'] != "OK":
                abort(400, description="Unable to calculate distance")
        except Exception as e:
            flash(f'Error calculating distance: {str(e)}', 'danger')
            return redirect(url_for('user.modify_booking', booking_id=booking_id))

        car = Car.query.get(car_id)
        if not car:
            flash('Selected car not available', 'danger')
            return redirect(url_for('user.modify_booking', booking_id=booking_id))

        distance_value = result['rows'][0]['elements'][0]['distance']['value']  # in meters
        duration_value = result['rows'][0]['elements'][0]['duration']['value']  # in seconds

        # Calculate fare
        distance_km = distance_value / 1000
        duration_min = duration_value / 60
        fare = BASE_FARE + (distance_km * car.rate_per_km) + (duration_min * TIME_RATE)

        try:
            # Store original values for the email
            original_booking_data = {
                'pickup_address': booking.pickup_address,
                'dropoff_address': booking.dropoff_address,
                'journey_date': booking.journey_date,
                'car_model': booking.vehicle.model,
                'estimated_fare': booking.estimated_fare
            }

            # Update booking with new values
            booking.pickup_latitude = pickup_lat
            booking.pickup_longitude = pickup_lng
            booking.pickup_address = pickup_address
            booking.dropoff_latitude = dropoff_lat
            booking.dropoff_longitude = dropoff_lng
            booking.dropoff_address = dropoff_address
            booking.journey_date = booking_datetime
            booking.car_id = car_id
            booking.estimated_fare = fare
            booking.status = 'modified'  # Change status to modified

            db.session.commit()

            # Send modification confirmation email
            email_sent = send_booking_modification_email(
                current_user,
                booking,
                car,
                fare,
                original_booking_data
            )

            if email_sent:
                flash('Booking modified successfully! A confirmation email has been sent to your email address.', 'success')
            else:
                flash('Booking modified successfully! However, we could not send the confirmation email.', 'warning')

            return redirect(url_for('user.dashboard'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('user.modify_booking', booking_id=booking_id))

    # GET request - show modification form with current booking details
    return render_template(
        'user/modify_booking.html', 
        booking=booking,
        cars=cars,
        google_maps_api_key = google_maps_api_key
    )
