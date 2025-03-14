"""This module defines the database models for the application."""
import re
from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager, bcrypt

@login_manager.user_loader
def load_user(user_id):
    # Check if user_id starts with "admin_" or "user_"
    if user_id.startswith("admin_"):
        user_id = user_id[6:]  # Remove "admin_" prefix
        return Admin.query.get(int(user_id))
    user_id = user_id[5:]  # Remove "user_" prefix
    return User.query.get(int(user_id))

class Admin(db.Model, UserMixin):
    """
    Admin details store in the application.

    Attributes:
        id (int): Primary key.
        usernme(str): Admin username.
        password_hash(str):  User password
    """
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
    """
    User details store in the application.

    Attributes:
        id (int): Primary key.
        name (str): User's name
        email (str): User's email address.
        phone(str): User's phone number.
        usernme(str): Unique username.
        password_hash(str):  User password
        created_at(dt): Time of account creation.
        bookings: User's cab bookings.
    """
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
    """
    Vehicle details store in the application.

    Attributes:
        id (int): Primary key.
        model (str): Car's name
        registration_number (str): Car's registration number
        capacity(int): Car's seating capacity
        rate_per_km(float): Car's fare per km
        is_available(bool):  Whether car is available or not
        created_at: Time of account creation.
        bookings: User's cab bookings.
    """
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    rate_per_km = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    bookings = db.relationship('Booking', back_populates='vehicle', lazy=True)

class Booking(db.Model):
    """
    Booking details store in the application.

    Attributes:
        id (int): Primary key.
        user_id (int): User's uuid
        car_id (int): Car's uuid
        pickup_latitude(float): Pickup location's latitude
        pickup_longitude(float): Pickup location's longitude
        pickup_address(str):  User's pickup address
        dropoff_latitude(float): Dropoff location's latitude
        dropoff_longitude(float): Dropoff location's longitude
        dropoff_address(str):  User's dropoff address
        booking_time(dt): Time of cab booking.
        journey_date(dt): Time of user's journey
        status(str): User's cab booking status.
        fare(float): Base Cab charges
        distance(int): Distance from pickup to dropoff location
        duration(int): How long will it take to reach
        estimated_fare(float): Cab charges as per car selection.
    """
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
    status = db.Column(db.String(20), default='confirmed')  # confirmed, modified, cancelled
    fare = db.Column(db.Float)
    distance = db.Column(db.Integer)  # in meters
    duration = db.Column(db.Integer)  # in seconds
    estimated_fare = db.Column(db.Float)
    # Relationships - use overlaps parameter to avoid the warning
    passenger = db.relationship('User', back_populates='bookings', overlaps="user,bookings")
    vehicle = db.relationship('Car', back_populates='bookings')
