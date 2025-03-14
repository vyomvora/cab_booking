"""This module defines admin's route for their functions"""
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Car
from app import db

admin = Blueprint('admin', __name__)

# Custom decorator to check if user is admin
def admin_required(f):
    """
    This function makes sure that only admin can access the panel.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    """
    This function is for admin dashboard.
    """
    cars = Car.query.all()
    return render_template('admin/admin_dashboard.html', cars=cars)

@admin.route('/admin/add_car', methods=['GET', 'POST'])
@login_required
@admin_required
def add_car():
    """
    This function lets admin add car.
    """
    if request.method == 'POST':
        model = request.form.get('model')
        registration_number = request.form.get('registration_number')
        capacity = request.form.get('capacity')
        rate_per_km = request.form.get('rate_per_km')

        # Validation
        if Car.query.filter_by(registration_number=registration_number).first():
            flash('Car with this registration number already exists', 'danger')
            return render_template('admin/add_car.html')

        try:
            car = Car(
                model=model,
                registration_number=registration_number,
                capacity=int(capacity),
                rate_per_km=float(rate_per_km),
                is_available=True
            )
            db.session.add(car)
            db.session.commit()
            flash('Car added successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding car: {str(e)}', 'danger')

    return render_template('admin/add_car.html')

@admin.route('/admin/delete_car/<int:car_id>', methods=['POST'])
@login_required
@admin_required
def delete_car(car_id):
    """
    This function lets admin delete selected car.
    """
    car = Car.query.get_or_404(car_id)
    try:
        db.session.delete(car)
        db.session.commit()
        flash('Car deleted successfully', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting car: {str(e)}', 'danger')

    return redirect(url_for('admin.dashboard'))
