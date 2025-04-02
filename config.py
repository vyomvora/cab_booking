"""This module defines the configuration of the database."""
import os
from datetime import timedelta

class Config:
    """
    This class defines the database setup for the application"
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cab_booking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    GOOGLE_MAPS_API_KEY = "CONFIG_GOOGLE_MAPS_API_KEY"
