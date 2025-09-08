import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_home_without_session(client):
    """Test akses / tanpa session"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"chat.html" in response.data or b"connection" in response.data

def test_login_invalid_input(client):
    """Test login tanpa input"""
    response = client.post("/login", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Input tidak valid"

def test_login_unregistered(client, monkeypatch):
    """Test login dengan user tidak terdaftar"""
    def fake_login_service(email): return False
    monkeypatch.setattr("app.login_service", fake_login_service)

    response = client.post("/login", json={"question": "unknown@example.com"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["isLogin"] is False

def test_logout(client):
    """Test logout"""
    with client.session_transaction() as sess:
        sess["session_id"] = "dummy"
    response = client.get("/logout")
    data = response.get_json()
    assert response.status_code == 200
    assert data["isLogin"] is False

def test_reset(client):
    """Test reset menghapus session"""
    with client.session_transaction() as sess:
        sess["session_id"] = "dummy"
    response = client.get("/reset")
    assert response.status_code == 302  # redirect ke home
    assert b"/" in response.data or response.location.endswith("/")
