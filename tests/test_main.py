"""
Starter tests for Museum Ancient Objects API
Run with: pytest tests/ -v
"""
from fastapi.testclient import TestClient
import sys
import os

# Make sure main.py is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)


# ─── Root ────────────────────────────────────────────────────────────────────

def test_root_returns_welcome():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# ─── GET all objects ─────────────────────────────────────────────────────────

def test_get_all_objects_returns_list():
    response = client.get("/objects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_all_objects_has_10_items():
    response = client.get("/objects")
    assert len(response.json()) == 10


# ─── GET single object ───────────────────────────────────────────────────────

def test_get_existing_object():
    response = client.get("/objects/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Rosetta Stone"

def test_get_nonexistent_object_returns_404():
    response = client.get("/objects/9999")
    assert response.status_code == 404


# ─── POST create object ──────────────────────────────────────────────────────

def test_create_object():
    new_obj = {
        "name": "Test Artifact",
        "origin": "Greece",
        "period": "500 BC",
        "material": "Bronze",
        "description": "A test artifact for automated testing",
        "status": "displayed"
    }
    response = client.post("/objects", json=new_obj)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Artifact"
    assert "id" in data

def test_create_object_invalid_status():
    new_obj = {
        "name": "Bad Artifact",
        "origin": "Unknown",
        "period": "Unknown",
        "material": "Unknown",
        "description": "Should fail",
        "status": "invalid-status"   # not a valid ObjectStatus
    }
    response = client.post("/objects", json=new_obj)
    assert response.status_code == 422  # FastAPI validation error


# ─── PATCH status ────────────────────────────────────────────────────────────

def test_update_object_status():
    response = client.patch("/objects/1/status", json={"status": "in-restoration"})
    assert response.status_code == 200
    assert response.json()["status"] == "in-restoration"

def test_update_status_nonexistent_object():
    response = client.patch("/objects/9999/status", json={"status": "displayed"})
    assert response.status_code == 404


# ─── GET object status ───────────────────────────────────────────────────────

def test_get_object_status():
    response = client.get("/objects/1/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "id" in data

def test_get_status_nonexistent_object():
    response = client.get("/objects/9999/status")
    assert response.status_code == 404


# ─── DELETE ──────────────────────────────────────────────────────────────────

def test_delete_object():
    # First create one to delete
    new_obj = {
        "name": "To Be Deleted",
        "origin": "Egypt",
        "period": "1000 BC",
        "material": "Clay",
        "description": "Temporary artifact",
        "status": "displayed"
    }
    create_resp = client.post("/objects", json=new_obj)
    created_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/objects/{created_id}")
    assert delete_resp.status_code == 204

def test_delete_nonexistent_object():
    response = client.delete("/objects/9999")
    assert response.status_code == 404