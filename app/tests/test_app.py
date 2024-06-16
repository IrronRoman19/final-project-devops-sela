import pytest
import sys
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, get_db

# Connect to testing database in MongoDB
@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    app.config['MONGO_DB_NAME'] = 'task_db_test'
    with app.test_client() as client:
        yield client

# Get testing database in MongoDB
@pytest.fixture(scope='module')
def db():
    with app.app_context():
        db = get_db()
        yield db
        client = db.client
        client.drop_database('task_db_test')

# Setup test database in MongoDB
@pytest.fixture(autouse=True)
def setup_database(db):
    tasks_collection = db.tasks
    tasks_collection.insert_many([
        {'full_name': 'John Doe', 'task_name': 'Test Task 1', 'description': 'Description 1', 'destination': '2024-05-23T12:00', 'creation_date': '2024-05-23 10:00', 'completed': False},
        {'full_name': 'Jane Smith', 'task_name': 'Test Task 2', 'description': 'Description 2', 'destination': '2024-05-24T12:00', 'creation_date': '2024-05-23 11:00', 'completed': False}
    ])
    yield
    tasks_collection.delete_many({})

# Test count total items
def test_count_created_items(client):
    response = client.get('/count')
    assert response.status_code == 200
    assert b'2' in response.data

# Test count completed items
def test_count_completed_items(client):
    response = client.get('/count_completed')
    assert response.status_code == 200
    assert b'0' in response.data

# Test count uncompleted items
def test_count_uncompleted_items(client):
    response = client.get('/count_uncompleted')
    assert response.status_code == 200
    assert b'2' in response.data

# Test home page
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Task App' in response.data

# Test create task
def test_create_task(client):
    response = client.post('/create', data={
        'full_name': 'John Doe',
        'task_name': 'New Task',
        'description': 'New Description',
        'destination': '2024-05-25T12:00'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'New Task' in response.data

# Test edit task
def test_edit_task(client):
    with app.app_context():
        task_id = get_db().tasks.find_one({'full_name': 'John Doe'})['_id']
    response = client.post(f'/edit/{task_id}', data={
        'full_name': 'John Doe',
        'task_name': 'Updated Task',
        'description': 'Updated Description',
        'destination': '2024-05-26T12:00'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Updated Task' in response.data

# Test complete task
def test_complete_task(client):
    with app.app_context():
        task_id = get_db().tasks.find_one({'full_name': 'John Doe'})['_id']
    response = client.get(f'/complete/{task_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Completed' in response.data

# Test uncomplete task
def test_uncomplete_task(client):
    with app.app_context():
        task_id = get_db().tasks.find_one({'full_name': 'John Doe'})['_id']
    response = client.get(f'/uncomplete/{task_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Pending' in response.data

# Test delete task
def test_delete_task(client):
    with app.app_context():
        task_id = get_db().tasks.find_one({'full_name': 'John Doe'})['_id']
    response = client.get(f'/delete/{task_id}', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        task = get_db().tasks.find_one({'_id': ObjectId(task_id)})
        assert task is None
