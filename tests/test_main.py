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
    # Test new maintenance fields
    assert "last_maintenance_date" in data
    assert "maintenance_interval_days" in data
    assert "condition_score" in data
    assert "maintenance_priority" in data
    assert "fragile" in data
    assert "environmental_sensitivity" in data

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


# ─── MAINTENANCE: Get History ────────────────────────────────────────────────

def test_get_maintenance_history_for_object():
    """Test getting maintenance history for an object with existing records"""
    response = client.get("/objects/5/maintenance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Object 5 (Dead Sea Scrolls) has 1 maintenance record in demo data
    assert len(data) >= 1
    if len(data) > 0:
        assert data[0]["object_id"] == 5
        assert "type" in data[0]
        assert "technician" in data[0]

def test_get_maintenance_history_nonexistent_object():
    """Test getting maintenance history for non-existent object"""
    response = client.get("/objects/9999/maintenance")
    assert response.status_code == 404

def test_get_maintenance_history_empty():
    """Test getting maintenance history for object with no records"""
    response = client.get("/objects/4/maintenance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ─── MAINTENANCE: Schedule Task ──────────────────────────────────────────────

def test_schedule_maintenance():
    """Test scheduling a new maintenance task"""
    maintenance_data = {
        "type": "cleaning",
        "scheduled_date": "2026-04-01",
        "technician": "Test Technician",
        "notes": "Test maintenance task",
        "estimated_duration_hours": 2,
        "cost_estimate": 250.0
    }
    response = client.post("/objects/1/maintenance", json=maintenance_data)
    assert response.status_code == 201
    data = response.json()
    assert data["object_id"] == 1
    assert data["type"] == "cleaning"
    assert data["technician"] == "Test Technician"
    assert data["completed"] == False
    assert data["completed_date"] is None
    assert "id" in data

def test_schedule_maintenance_nonexistent_object():
    """Test scheduling maintenance for non-existent object"""
    maintenance_data = {
        "type": "inspection",
        "scheduled_date": "2026-04-01",
        "technician": "Test Technician",
        "notes": "Should fail"
    }
    response = client.post("/objects/9999/maintenance", json=maintenance_data)
    assert response.status_code == 404

def test_schedule_maintenance_minimal_data():
    """Test scheduling maintenance with minimal required fields"""
    maintenance_data = {
        "type": "inspection",
        "scheduled_date": "2026-04-15",
        "technician": "Jane Doe",
        "notes": "Minimal test"
    }
    response = client.post("/objects/2/maintenance", json=maintenance_data)
    assert response.status_code == 201
    data = response.json()
    assert data["estimated_duration_hours"] == 2  # default value
    assert data["cost_estimate"] is None


# ─── MAINTENANCE: Get Pending ────────────────────────────────────────────────

def test_get_pending_maintenance():
    """Test getting all pending maintenance tasks"""
    response = client.get("/maintenance/pending")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Verify all returned items are not completed
    for record in data:
        assert record["completed"] == False
        assert "object_id" in record
        assert "type" in record
        assert "scheduled_date" in record

def test_pending_maintenance_excludes_completed():
    """Test that completed maintenance is not in pending list"""
    response = client.get("/maintenance/pending")
    assert response.status_code == 200
    pending = response.json()
    # Check that record ID 3 (completed in demo data) is not in pending
    pending_ids = [r["id"] for r in pending]
    assert 3 not in pending_ids  # Record 3 is completed
    assert 6 not in pending_ids  # Record 6 is completed
    assert 8 not in pending_ids  # Record 8 is completed


# ─── MAINTENANCE: Complete Task ──────────────────────────────────────────────

def test_complete_maintenance():
    """Test marking a maintenance task as complete"""
    # First create a maintenance record
    maintenance_data = {
        "type": "cleaning",
        "scheduled_date": "2026-03-20",
        "technician": "Test Tech",
        "notes": "To be completed"
    }
    create_resp = client.post("/objects/6/maintenance", json=maintenance_data)
    record_id = create_resp.json()["id"]
    
    # Now complete it
    completion_data = {"completed_date": "2026-03-20"}
    response = client.patch(f"/maintenance/{record_id}/complete", json=completion_data)
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] == True
    assert data["completed_date"] == "2026-03-20"

def test_complete_maintenance_auto_date():
    """Test completing maintenance without providing date (uses current date)"""
    # Create a maintenance record
    maintenance_data = {
        "type": "inspection",
        "scheduled_date": "2026-03-21",
        "technician": "Auto Date Test",
        "notes": "Testing auto date"
    }
    create_resp = client.post("/objects/7/maintenance", json=maintenance_data)
    record_id = create_resp.json()["id"]
    
    # Complete without date
    response = client.patch(f"/maintenance/{record_id}/complete", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] == True
    assert data["completed_date"] is not None

def test_complete_maintenance_nonexistent():
    """Test completing non-existent maintenance record"""
    response = client.patch("/maintenance/99999/complete", json={})
    assert response.status_code == 404

def test_complete_already_completed_maintenance():
    """Test completing a maintenance task that's already completed"""
    # Record 3 is already completed in demo data
    response = client.patch("/maintenance/3/complete", json={"completed_date": "2026-03-02"})
    assert response.status_code == 400

def test_complete_maintenance_updates_object():
    """Test that completing maintenance updates object's last_maintenance_date"""
    # Create and complete maintenance
    maintenance_data = {
        "type": "cleaning",
        "scheduled_date": "2026-03-25",
        "technician": "Object Update Test",
        "notes": "Testing object update"
    }
    create_resp = client.post("/objects/4/maintenance", json=maintenance_data)
    record_id = create_resp.json()["id"]
    
    # Complete it
    completion_data = {"completed_date": "2026-03-25"}
    client.patch(f"/maintenance/{record_id}/complete", json=completion_data)
    
    # Check object was updated
    obj_response = client.get("/objects/4")
    obj_data = obj_response.json()
    assert obj_data["last_maintenance_date"] == "2026-03-25"


# ─── MAINTENANCE: Objects Requiring Maintenance ──────────────────────────────

def test_get_objects_requiring_maintenance():
    """Test getting objects that need maintenance"""
    response = client.get("/objects/requiring-maintenance")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "objects" in data
    assert isinstance(data["objects"], list)
    
    # Verify structure of returned objects
    if data["count"] > 0:
        obj = data["objects"][0]
        assert "id" in obj
        assert "name" in obj
        assert "status" in obj
        assert "condition_score" in obj
        assert "maintenance_priority" in obj
        assert "reasons" in obj
        assert isinstance(obj["reasons"], list)

def test_objects_requiring_maintenance_has_reasons():
    """Test that objects requiring maintenance have valid reasons"""
    response = client.get("/objects/requiring-maintenance")
    data = response.json()
    
    for obj in data["objects"]:
        assert len(obj["reasons"]) > 0
        # Check for expected reason patterns
        reasons_text = " ".join(obj["reasons"])
        has_valid_reason = any([
            "overdue" in reasons_text.lower(),
            "condition score" in reasons_text.lower(),
            "priority level" in reasons_text.lower(),
            "fragile" in reasons_text.lower()
        ])
        assert has_valid_reason

def test_objects_requiring_maintenance_includes_urgent():
    """Test that urgent priority objects are flagged for maintenance"""
    response = client.get("/objects/requiring-maintenance")
    data = response.json()
    
    # Object 5 (Dead Sea Scrolls) has urgent priority
    object_ids = [obj["id"] for obj in data["objects"]]
    assert 5 in object_ids


# ─── MAINTENANCE: Integration Tests ──────────────────────────────────────────

def test_full_maintenance_workflow():
    """Test complete maintenance workflow from scheduling to completion"""
    # 1. Check object needs maintenance
    needs_maint = client.get("/objects/requiring-maintenance")
    initial_count = needs_maint.json()["count"]
    
    # 2. Schedule maintenance
    schedule_resp = client.post("/objects/1/maintenance", json={
        "type": "restoration",
        "scheduled_date": "2026-04-10",
        "technician": "Workflow Test",
        "notes": "Full workflow test",
        "estimated_duration_hours": 4,
        "cost_estimate": 1000.0
    })
    assert schedule_resp.status_code == 201
    record_id = schedule_resp.json()["id"]
    
    # 3. Verify it appears in pending
    pending = client.get("/maintenance/pending")
    pending_ids = [r["id"] for r in pending.json()]
    assert record_id in pending_ids
    
    # 4. Complete the maintenance
    complete_resp = client.patch(f"/maintenance/{record_id}/complete", json={
        "completed_date": "2026-04-10"
    })
    assert complete_resp.status_code == 200
    
    # 5. Verify it's no longer in pending
    pending_after = client.get("/maintenance/pending")
    pending_ids_after = [r["id"] for r in pending_after.json()]
    assert record_id not in pending_ids_after
    
    # 6. Verify it's in object's history
    history = client.get("/objects/1/maintenance")
    history_ids = [r["id"] for r in history.json()]
    assert record_id in history_ids