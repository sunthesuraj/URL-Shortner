import pytest
from app.main import app

@pytest.fixture
def client():
    """Pytest fixture to create a test client for the app."""
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Tests the health check endpoint as you specified."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'

def test_shorten_success(client):
    """Test successful URL shortening."""
    response = client.post('/api/shorten', json={"url": "https://www.google.com/search?q=flask"})
    assert response.status_code == 201
    data = response.get_json()
    assert 'short_code' in data
    assert 'short_url' in data
    assert len(data['short_code']) == 6
    assert data['short_url'].endswith(data['short_code'])

def test_shorten_invalid_url(client):
    """Test shortening with an invalid URL string."""
    response = client.post('/api/shorten', json={"url": "this-is-not-a-url"})
    assert response.status_code == 400
    assert response.get_json()['error'] == "Invalid URL provided"

def test_shorten_missing_key(client):
    """Test shortening with a missing 'url' key in the JSON payload."""
    response = client.post('/api/shorten', json={"some_other_key": "value"})
    assert response.status_code == 400
    assert response.get_json()['error'] == "Missing 'url' key in request body"

def test_shorten_not_json(client):
    """Test shortening with a request body that is not JSON."""
    response = client.post('/api/shorten', data="plain text", content_type="text/plain")
    assert response.status_code == 400
    assert response.get_json()['error'] == "Invalid JSON format"

def test_redirect_and_stats_flow(client):
    """Tests the full flow: shorten, redirect, and check stats."""
    long_url = "https://www.python.org/psf/"
    post_response = client.post('/api/shorten', json={"url": long_url})
    assert post_response.status_code == 201
    short_code = post_response.get_json()['short_code']

    redirect_response = client.get(f'/{short_code}')
    assert redirect_response.status_code == 302
    assert redirect_response.location == long_url

    stats_response = client.get(f'/api/stats/{short_code}')
    assert stats_response.status_code == 200
    stats_data = stats_response.get_json()
    assert stats_data['url'] == long_url
    assert stats_data['clicks'] == 1
    assert 'created_at' in stats_data

    client.get(f'/{short_code}')
    stats_response_2 = client.get(f'/api/stats/{short_code}')
    assert stats_response_2.status_code == 200
    assert stats_response_2.get_json()['clicks'] == 2

def test_redirect_not_found(client):
    """Test redirecting a short code that does not exist."""
    response = client.get('/abcdef')
    assert response.status_code == 404
    assert response.get_json()['error'] == "Not Found"

def test_stats_not_found(client):
    """Test getting stats for a short code that does not exist."""
    response = client.get('/api/stats/abcdef')
    assert response.status_code == 404
    assert response.get_json()['error'] == "Not Found"