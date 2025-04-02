from app.models import User, Admin
from werkzeug.security import generate_password_hash

def test_admin_login(test_client, init_database):
    # Test successful admin login
    response = test_client.post('/admin/login', data=dict(
        username='admin',
        password= generate_password_hash('Admin@123')
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_user_login(test_client, init_database):
    # Test successful user login
    response = test_client.post('/login', data=dict(
        username='testuser',
        password='hashed_password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'User Dashboard' in response.data

def test_user_signup(test_client, init_database):
    # Test user signup
    response = test_client.post('/signup', data=dict(
        name='New User',
        email='new@example.com',
        phone='9876543210',
        username='newuser',
        password='HashPass@123',
        confirm_password='HashPass@123'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert User.query.filter_by(username='newuser').first() is not None