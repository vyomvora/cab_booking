from flask import url_for
from app.models import Car

def test_admin_dashboard(test_client, init_database):
    # Test admin dashboard access
    with test_client.session_transaction() as sess:
        sess['user_id'] = 'admin_1'
    response = test_client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_add_car(test_client, init_database):
    # Test adding a new car
    with test_client.session_transaction() as sess:
        sess['user_id'] = 'admin_1'
    response = test_client.post('/admin/add_car', data=dict(
        model='New Model',
        capacity=5,
        rate_per_km=2.0
    ), follow_redirects=True)
    assert response.status_code == 200
    assert Car.query.filter_by(model='New Model').first() is not None

def test_delete_car(test_client, init_database):
    # Test deleting a car
    with test_client.session_transaction() as sess:
        sess['user_id'] = 'admin_1'
    car = Car.query.first()
    response = test_client.post(f'/admin/delete_car/{car.id}', follow_redirects=True)
    assert response.status_code == 200
    assert Car.query.get(car.id) is None