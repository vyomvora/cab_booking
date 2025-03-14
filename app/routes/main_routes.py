"""This module defines the home route for the application"""
from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')

def home():
    """
    This function routes to the home page of application
    """
    return render_template('home.html')
