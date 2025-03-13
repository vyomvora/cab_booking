from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.models import Admin, User
from app import db
import re

auth = Blueprint('auth', __name__)

@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and getattr(current_user, 'get_id', lambda: '')().startswith('admin_'):
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('auth/admin_login.html')

@auth.route('/login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated and getattr(current_user, 'get_id', lambda: '')().startswith('user_'):
        return redirect(url_for('user.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user.dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('auth/user_login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def user_signup():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('auth/user_signup.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('auth/user_signup.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/user_signup.html')
            
        # Password validation
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return render_template('auth/user_signup.html')
            
        if not re.search(r'\d', password):
            flash('Password must contain at least one number', 'danger')
            return render_template('auth/user_signup.html')
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must contain at least one special character', 'danger')
            return render_template('auth/user_signup.html')
            
        # Create new user
        user = User(name=name, email=email, phone=phone, username=username)
        try:
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in', 'success')
            return redirect(url_for('auth.user_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')
    
    return render_template('auth/user_signup.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.user_login'))