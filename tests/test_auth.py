import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db, User, SessionLocal

client = TestClient(app)

@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
def create_user(db):
    user = User(username="testuser", role="viewer")
    user.set_password("testpassword")
    db.add(user)
    db.commit()

def test_signup(db):
    response = client.post("/auth/signup", json={"username": "newuser", "password": "newpass"})
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

def test_login(create_user):
    response = client.post("/auth/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
