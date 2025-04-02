from datetime import datetime
from app.email_templates import send_booking_confirmation, send_booking_modification_email, send_booking_cancellation_email
from app.models import User, Booking, Car
from unittest.mock import patch

def test_send_booking_confirmation(test_client, init_database):
    user = User.query.first()
    car = Car.query.first()
    booking = Booking(
        user_id=user.id,
        car_id=car.id,
        pickup_address='Test Pickup',
        dropoff_address='Test Dropoff',
        journey_date=datetime.now(),
        status='confirmed',
        estimated_fare=100.0
    )
    
    with patch('smtplib.SMTP') as mock_smtp:
        result = send_booking_confirmation(user, booking, car, 100.0)
        assert result is True
        assert mock_smtp.called

def test_send_booking_modification_email(test_client, init_database):
    user = User.query.first()
    car = Car.query.first()
    booking = Booking(
        user_id=user.id,
        car_id=car.id,
        pickup_address='Test Pickup',
        dropoff_address='Test Dropoff',
        journey_date=datetime.now(),
        status='modified',
        estimated_fare=100.0
    )
    
    with patch('smtplib.SMTP') as mock_smtp:
        result = send_booking_modification_email(
            user, 
            booking, 
            car, 
            100.0,
            {
                'pickup_address': 'Old Pickup',
                'dropoff_address': 'Old Dropoff',
                'journey_date': datetime.now(),
                'car_model': 'Old Model',
                'estimated_fare': 80.0
            }
        )
        assert result is True
        assert mock_smtp.called