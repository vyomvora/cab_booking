from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime
import re

@login_manager.user_loader
def load_user(user_id):
    # Check if user_id starts with "admin_" or "user_"
    if user_id.startswith("admin_"):
        user_id = user_id[6:]  # Remove "admin_" prefix
        return Admin.query.get(int(user_id))
    else:
        user_id = user_id[5:]  # Remove "user_" prefix
        return User.query.get(int(user_id))

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def get_id(self):
        return f"admin_{self.id}"
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', back_populates='passenger', lazy=True)

    def get_id(self):
        return f"user_{self.id}"
    
    def set_password(self, password):
        # Validate password
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")
            
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    rate_per_km = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    bookings = db.relationship('Booking', back_populates='vehicle', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    
    pickup_latitude = db.Column(db.Float, nullable=True)
    pickup_longitude = db.Column(db.Float, nullable=True)
    pickup_address = db.Column(db.String(255), nullable=True)
    
    dropoff_latitude = db.Column(db.Float, nullable=True)
    dropoff_longitude = db.Column(db.Float, nullable=True)
    dropoff_address = db.Column(db.String(255), nullable=True)
    
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    journey_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    fare = db.Column(db.Float)
    distance = db.Column(db.Integer)  # in meters
    duration = db.Column(db.Integer)  # in seconds
    estimated_fare = db.Column(db.Float)        # in dollars
    
    # Relationships - use overlaps parameter to avoid the warning
    passenger = db.relationship('User', back_populates='bookings', overlaps="user,bookings")
    vehicle = db.relationship('Car', back_populates='bookings')