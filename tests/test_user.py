from flask import url_for
from app.models import Booking, Car
from app import db
from datetime import datetime, timedelta

def test_user_dashboard(test_client, init_database):
    # Test user dashboard access
    with test_client.session_transaction() as sess:
        sess['user_id'] = 'user_1'
    response = test_client.get('/dashboard')
    assert response.status_code == 200
    assert b'User Dashboard' in response.data

def test_book_cab(test_client, init_database):
    # Test booking a cab
    with test_client.session_transaction() as sess:
        sess['user_id'] = 'user_1'
    future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = test_client.post('/book_cab', data=dict(
        pickup_lat='12.9716',
        pickup_lng='77.5946',
        pickup_address='Bangalore',
        dropoff_lat='13.0827',
        dropoff_lng='80.2707',
        dropoff_address='Chennai',
        date=future_date,
        time='12:00',
        car_type=1
    ), follow_redirects=True)
    assert response.status_code == 200
    assert Booking.query.filter_by(user_id=1).first() is not None

def test_cancel_booking(test_client, init_database):
    # Test canceling a booking
    with test_client.session_transaction() as sess:
        sess['user_id'] = 'user_1'
    # Create a booking first
    booking = Booking(
        user_id=1,
        car_id=1,
        pickup_address='Test Pickup',
        dropoff_address='Test Dropoff',
        journey_date=datetime.now() + timedelta(days=1),
        status='confirmed'
    )
    db.session.add(booking)
    db.session.commit()
    
    response = test_client.post(f'/cancel_booking/{booking.id}', follow_redirects=True)
    assert response.status_code == 200
    assert Booking.query.get(booking.id).status == 'cancelled'