import pytest
from app import create_app, db
from app.models import User, Admin, Car, Booking
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()

from werkzeug.security import generate_password_hash

@pytest.fixture(scope='function')
def init_database(test_client):
    # Clear database before each test
    db.session.query(Admin).delete()
    db.session.query(User).delete()
    db.session.query(Car).delete()
    db.session.commit()

    # Create test admin
    admin = Admin(
        username='admin',
        password_hash=generate_password_hash('Admin@123')  # Correct hashing
    )

    # Create test user
    user = User(
        name='Test User',
        email='test@example.com',
        phone='1234567890',
        username='testuser',
        password_hash=generate_password_hash('hashed_password')  # Correct hashing
    )

    # Create test car
    car = Car(
        model='Test Model',
        capacity=4,
        rate_per_km=1.5,
        is_available=True
    )

    db.session.add(admin)
    db.session.add(user)
    db.session.add(car)
    db.session.commit()

    yield

    db.session.rollback()


