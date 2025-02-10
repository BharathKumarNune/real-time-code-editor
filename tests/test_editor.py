import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_debug_code():
    response = client.post("/editor/debug", json={"code": "print('Hello World')"})
    assert response.status_code == 200
    assert "suggestions" in response.json()
