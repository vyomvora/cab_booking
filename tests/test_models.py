from app.models import User, Admin, Car, Booking
from app import db
from datetime import datetime

def test_user_model(test_client, init_database):
    user = User.query.filter_by(username='testuser').first()
    assert user.email == 'test@example.com'
    assert user.get_id() == 'user_1'

def test_admin_model(test_client, init_database):
    admin = Admin.query.filter_by(username='testadmin').first()
    assert admin.get_id() == 'admin_1'

def test_car_model(test_client, init_database):
    car = Car.query.first()
    assert car.model == 'Test Model'
    assert car.is_available == True

def test_booking_model(test_client, init_database):
    booking = Booking(
        user_id=1,
        car_id=1,
        pickup_address='Test Pickup',
        dropoff_address='Test Dropoff',
        journey_date=datetime.now(),
        status='confirmed'
    )
    db.session.add(booking)
    db.session.commit()
    assert booking.passenger.username == 'testuser'
    assert booking.vehicle.model == 'Test Model'