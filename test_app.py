"""
Tests for OnlyFringe Platform
"""
import pytest
import json
from app import app, db
from models import User, Argument, Source, Rebuttal, RebuttalSource

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def sample_user(client):
    """Create a sample user"""
    response = client.post('/api/users', 
        json={'username': 'testuser', 'email': 'test@example.com'},
        content_type='application/json')
    return response.get_json()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'database' in data
    assert 'ai_enabled' in data

def test_create_user(client):
    """Test user creation"""
    response = client.post('/api/users',
        json={'username': 'john_doe', 'email': 'john@example.com'},
        content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == 'john_doe'
    assert data['email'] == 'john@example.com'
    assert 'id' in data
    assert 'created_at' in data

def test_create_user_duplicate(client, sample_user):
    """Test creating duplicate user fails"""
    response = client.post('/api/users',
        json={'username': 'testuser', 'email': 'test@example.com'},
        content_type='application/json')
    
    assert response.status_code == 409
    data = response.get_json()
    assert 'error' in data

def test_create_user_missing_fields(client):
    """Test creating user without required fields"""
    response = client.post('/api/users',
        json={'username': 'john_doe'},
        content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_get_user(client, sample_user):
    """Test getting user information"""
    user_id = sample_user['id']
    response = client.get(f'/api/users/{user_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == user_id
    assert data['username'] == 'testuser'

def test_submit_argument(client, sample_user):
    """Test submitting an argument"""
    argument_data = {
        'title': 'Test Argument',
        'content': 'This is a test argument with sufficient length to meet the minimum requirement. It presents a clear position supported by evidence and logical reasoning.',
        'category': 'test',
        'user_id': sample_user['id'],
        'sources': [
            {
                'url': 'https://example.com/source1',
                'title': 'Source 1',
                'description': 'First credible source'
            },
            {
                'url': 'https://example.com/source2',
                'title': 'Source 2',
                'description': 'Second credible source'
            }
        ]
    }
    
    response = client.post('/api/arguments',
        json=argument_data,
        content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Argument'
    assert 'fact_check' in data
    assert data['verification_status'] in ['approved', 'rejected', 'pending']

def test_submit_argument_insufficient_sources(client, sample_user):
    """Test submitting argument with insufficient sources"""
    argument_data = {
        'title': 'Test Argument',
        'content': 'This is a test argument.',
        'user_id': sample_user['id'],
        'sources': [
            {
                'url': 'https://example.com/source1',
                'title': 'Source 1',
                'description': 'Only one source'
            }
        ]
    }
    
    response = client.post('/api/arguments',
        json=argument_data,
        content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'sources' in data['error'].lower()

def test_submit_argument_too_short(client, sample_user):
    """Test submitting argument that's too short"""
    argument_data = {
        'title': 'Test',
        'content': 'Too short',
        'user_id': sample_user['id'],
        'sources': [
            {'url': 'https://example.com/1', 'title': 'S1', 'description': 'D1'},
            {'url': 'https://example.com/2', 'title': 'S2', 'description': 'D2'}
        ]
    }
    
    response = client.post('/api/arguments',
        json=argument_data,
        content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_submit_argument_invalid_url(client, sample_user):
    """Test submitting argument with invalid source URL"""
    argument_data = {
        'title': 'Test Argument',
        'content': 'This is a test argument with sufficient length to meet the minimum requirement. It includes all necessary information and context.',
        'user_id': sample_user['id'],
        'sources': [
            {
                'url': 'not-a-valid-url',
                'title': 'Invalid Source',
                'description': 'This has an invalid URL'
            },
            {
                'url': 'https://example.com/source2',
                'title': 'Valid Source',
                'description': 'This one is valid'
            }
        ]
    }
    
    response = client.post('/api/arguments',
        json=argument_data,
        content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'invalid' in data['error'].lower() or 'url' in data['error'].lower()

def test_list_arguments(client, sample_user):
    """Test listing arguments"""
    # Create an argument first
    argument_data = {
        'title': 'Test Argument',
        'content': 'This is a test argument with sufficient length to meet the minimum requirement.',
        'user_id': sample_user['id'],
        'sources': [
            {'url': 'https://example.com/1', 'title': 'S1', 'description': 'D1'},
            {'url': 'https://example.com/2', 'title': 'S2', 'description': 'D2'}
        ]
    }
    client.post('/api/arguments', json=argument_data, content_type='application/json')
    
    # List arguments
    response = client.get('/api/arguments')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_argument(client, sample_user):
    """Test getting a specific argument"""
    # Create an argument first
    argument_data = {
        'title': 'Test Argument',
        'content': 'This is a test argument with sufficient length to meet the minimum requirement. It provides complete context and logical reasoning.',
        'user_id': sample_user['id'],
        'sources': [
            {'url': 'https://example.com/1', 'title': 'S1', 'description': 'D1'},
            {'url': 'https://example.com/2', 'title': 'S2', 'description': 'D2'}
        ]
    }
    create_response = client.post('/api/arguments', json=argument_data, content_type='application/json')
    
    # Check if creation was successful
    assert create_response.status_code == 201
    response_data = create_response.get_json()
    assert 'id' in response_data
    argument_id = response_data['id']
    
    # Get the argument
    response = client.get(f'/api/arguments/{argument_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == argument_id
    assert data['title'] == 'Test Argument'

def test_api_endpoint(client):
    """Test API info endpoint"""
    response = client.get('/api')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'endpoints' in data
