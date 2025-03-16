"""This module defines admin's route for their functions"""
import re
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

@admin.route('/admin/admin_profile', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_profile():
    """
    This function allows admin to view and update their profile information.
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('admin.admin_profile'))
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('admin.admin_profile'))
            
        # Password validation
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return redirect(url_for('admin.admin_profile'))
            
        if not re.search(r'\d', new_password):
            flash('Password must contain at least one number', 'danger')
            return redirect(url_for('admin.admin_profile'))
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            flash('Password must contain at least one special character', 'danger')
            return redirect(url_for('admin.admin_profile'))
        
        try:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully', 'success')
            return redirect(url_for('admin.admin_profile'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error changing password: {str(e)}', 'danger')

    return render_template('admin/admin_profile.html')

@admin.route('/admin/add_car', methods=['GET', 'POST'])
@login_required
@admin_required
def add_car():
    """
    This function lets admin add car.
    """
    if request.method == 'POST':
        model = request.form.get('model')
        capacity = request.form.get('capacity')
        rate_per_km = request.form.get('rate_per_km')

        try:
            car = Car(
                model=model,
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
