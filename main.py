from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import threading
from datetime import datetime, timedelta

app = FastAPI(title="Museum Ancient Objects API")


class ObjectStatus(str, Enum):
    """Status of museum objects"""
    DISPLAYED = "displayed"
    IN_RESTORATION = "in-restoration"
    TO_OTHER_MUSEUM = "to-other-museum"


class MaintenancePriority(str, Enum):
    """Priority level for object maintenance"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EnvironmentalSensitivity(str, Enum):
    """Environmental sensitivity level of museum objects"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class MaintenanceType(str, Enum):
    """Type of maintenance activity"""
    CLEANING = "cleaning"
    RESTORATION = "restoration"
    INSPECTION = "inspection"
    PREVENTIVE = "preventive"


class MuseumObject(BaseModel):
    """Model for museum objects"""
    id: int
    name: str
    origin: str
    period: str
    material: str
    description: str
    status: ObjectStatus = ObjectStatus.DISPLAYED
    # Maintenance-related fields
    last_maintenance_date: Optional[str] = None
    maintenance_interval_days: int = 90  # Default: check every 90 days
    condition_score: int = 5  # 1-10, where 10 is perfect condition
    maintenance_priority: MaintenancePriority = MaintenancePriority.NORMAL
    fragile: bool = False
    environmental_sensitivity: EnvironmentalSensitivity = EnvironmentalSensitivity.NORMAL


class MuseumObjectCreate(BaseModel):
    """Model for creating museum objects"""
    name: str
    origin: str
    period: str
    material: str
    description: str
    status: ObjectStatus = ObjectStatus.DISPLAYED


class StatusUpdate(BaseModel):
    """Model for updating object status"""
    status: ObjectStatus


class MaintenanceRecord(BaseModel):
    """Model for maintenance records"""
    id: int
    object_id: int
    type: MaintenanceType  # "cleaning", "restoration", "inspection", "preventive"
    scheduled_date: str
    technician: str
    notes: str
    completed: bool = False
    completed_date: Optional[str] = None
    estimated_duration_hours: int = 2
    cost_estimate: Optional[float] = None


class MaintenanceRecordCreate(BaseModel):
    """Model for creating maintenance records"""
    type: MaintenanceType
    scheduled_date: str
    technician: str
    notes: str
    estimated_duration_hours: int = 2
    cost_estimate: Optional[float] = None


class MaintenanceComplete(BaseModel):
    """Model for marking maintenance as complete"""
    completed_date: Optional[str] = None


# In-memory storage with 10 ancient world objects
museum_objects = {
    1: MuseumObject(
        id=1,
        name="Rosetta Stone",
        origin="Egypt",
        period="196 BC",
        material="Granodiorite",
        description="Ancient Egyptian decree inscribed in three scripts",
        status=ObjectStatus.DISPLAYED,
        last_maintenance_date="2025-09-15",
        maintenance_interval_days=60,
        condition_score=7,
        maintenance_priority="high",
        fragile=False,
        environmental_sensitivity="normal"
    ),
    2: MuseumObject(
        id=2,
        name="Venus de Milo",
        origin="Greece",
        period="130-100 BC",
        material="Marble",
        description="Ancient Greek statue of Aphrodite",
        status=ObjectStatus.DISPLAYED,
        last_maintenance_date="2025-11-20",
        maintenance_interval_days=90,
        condition_score=8,
        maintenance_priority="normal",
        fragile=True,
        environmental_sensitivity="high"
    ),
    3: MuseumObject(
        id=3,
        name="Terracotta Army Warrior",
        origin="China",
        period="210-209 BC",
        material="Terracotta",
        description="Life-sized warrior from Emperor Qin's tomb",
        status=ObjectStatus.IN_RESTORATION,
        last_maintenance_date="2026-02-10",
        maintenance_interval_days=120,
        condition_score=6,
        maintenance_priority="normal",
        fragile=True,
        environmental_sensitivity="normal"
    ),
    4: MuseumObject(
        id=4,
        name="Code of Hammurabi",
        origin="Babylon",
        period="1754 BC",
        material="Basalt",
        description="Ancient Babylonian law code",
        status=ObjectStatus.DISPLAYED,
        last_maintenance_date="2025-12-01",
        maintenance_interval_days=180,
        condition_score=9,
        maintenance_priority="low",
        fragile=False,
        environmental_sensitivity="low"
    ),
    5: MuseumObject(
        id=5,
        name="Dead Sea Scrolls Fragment",
        origin="Israel",
        period="300 BC - 100 AD",
        material="Parchment",
        description="Ancient Jewish religious manuscript",
        status=ObjectStatus.IN_RESTORATION,
        last_maintenance_date="2026-01-05",
        maintenance_interval_days=30,
        condition_score=4,
        maintenance_priority="urgent",
        fragile=True,
        environmental_sensitivity="high"
    ),
    6: MuseumObject(
        id=6,
        name="Mask of Agamemnon",
        origin="Greece",
        period="1600-1500 BC",
        material="Gold",
        description="Mycenaean funeral mask",
        status=ObjectStatus.DISPLAYED,
        last_maintenance_date="2025-10-15",
        maintenance_interval_days=120,
        condition_score=9,
        maintenance_priority="normal",
        fragile=False,
        environmental_sensitivity="low"
    ),
    7: MuseumObject(
        id=7,
        name="Parthenon Frieze",
        origin="Greece",
        period="447-438 BC",
        material="Marble",
        description="Classical Greek sculptural decoration",
        status=ObjectStatus.TO_OTHER_MUSEUM,
        last_maintenance_date="2025-08-20",
        maintenance_interval_days=90,
        condition_score=7,
        maintenance_priority="high",
        fragile=True,
        environmental_sensitivity="high"
    ),
    8: MuseumObject(
        id=8,
        name="Nefertiti Bust",
        origin="Egypt",
        period="1345 BC",
        material="Limestone",
        description="Portrait of Egyptian Queen Nefertiti",
        status=ObjectStatus.DISPLAYED,
        last_maintenance_date="2025-11-30",
        maintenance_interval_days=75,
        condition_score=8,
        maintenance_priority="normal",
        fragile=True,
        environmental_sensitivity="normal"
    ),
    9: MuseumObject(
        id=9,
        name="Sumerian Cuneiform Tablet",
        origin="Mesopotamia",
        period="3200 BC",
        material="Clay",
        description="Early writing system example",
        status=ObjectStatus.IN_RESTORATION,
        last_maintenance_date="2026-02-15",
        maintenance_interval_days=60,
        condition_score=5,
        maintenance_priority="high",
        fragile=True,
        environmental_sensitivity="normal"
    ),
    10: MuseumObject(
        id=10,
        name="Olmec Colossal Head",
        origin="Mexico",
        period="1500-1000 BC",
        material="Basalt",
        description="Massive stone head sculpture",
        status=ObjectStatus.DISPLAYED,
        last_maintenance_date="2025-06-10",
        maintenance_interval_days=150,
        condition_score=8,
        maintenance_priority="normal",
        fragile=False,
        environmental_sensitivity="low"
    )
}

# In-memory storage for maintenance records with demo data
maintenance_records = {
    1: MaintenanceRecord(
        id=1,
        object_id=5,  # Dead Sea Scrolls Fragment
        type="inspection",
        scheduled_date="2026-03-15",
        technician="Dr. Sarah Chen",
        notes="Urgent inspection due to low condition score and environmental sensitivity",
        completed=False,
        estimated_duration_hours=3,
        cost_estimate=500.0
    ),
    2: MaintenanceRecord(
        id=2,
        object_id=1,  # Rosetta Stone
        type="cleaning",
        scheduled_date="2026-03-10",
        technician="John Smith",
        notes="Routine cleaning for high-traffic display item",
        completed=False,
        estimated_duration_hours=2,
        cost_estimate=200.0
    ),
    3: MaintenanceRecord(
        id=3,
        object_id=2,  # Venus de Milo
        type="preventive",
        scheduled_date="2026-03-05",
        technician="Maria Rodriguez",
        notes="Humidity control check for marble preservation",
        completed=True,
        completed_date="2026-03-05",
        estimated_duration_hours=1,
        cost_estimate=150.0
    ),
    4: MaintenanceRecord(
        id=4,
        object_id=9,  # Sumerian Cuneiform Tablet
        type="restoration",
        scheduled_date="2026-03-20",
        technician="Dr. Ahmed Hassan",
        notes="Fragment stabilization and documentation",
        completed=False,
        estimated_duration_hours=8,
        cost_estimate=2000.0
    ),
    5: MaintenanceRecord(
        id=5,
        object_id=10,  # Olmec Colossal Head
        type="inspection",
        scheduled_date="2026-03-08",
        technician="Carlos Mendez",
        notes="Check for weather damage from outdoor display",
        completed=False,
        estimated_duration_hours=2,
        cost_estimate=300.0
    ),
    6: MaintenanceRecord(
        id=6,
        object_id=7,  # Parthenon Frieze
        type="cleaning",
        scheduled_date="2026-02-28",
        technician="Dr. Elena Papadopoulos",
        notes="Pre-loan cleaning before transport to other museum",
        completed=True,
        completed_date="2026-02-28",
        estimated_duration_hours=4,
        cost_estimate=800.0
    ),
    7: MaintenanceRecord(
        id=7,
        object_id=8,  # Nefertiti Bust
        type="inspection",
        scheduled_date="2026-03-12",
        technician="Dr. Sarah Chen",
        notes="Fragile limestone assessment for display rotation",
        completed=False,
        estimated_duration_hours=2,
        cost_estimate=350.0
    ),
    8: MaintenanceRecord(
        id=8,
        object_id=3,  # Terracotta Army Warrior
        type="restoration",
        scheduled_date="2026-02-20",
        technician="Li Wei",
        notes="Terracotta surface stabilization and pigment preservation",
        completed=True,
        completed_date="2026-02-20",
        estimated_duration_hours=6,
        cost_estimate=1500.0
    )
}
next_maintenance_id = 9
maintenance_lock = threading.Lock()

# Counter for generating new IDs with thread-safe lock
next_id = 11
id_lock = threading.Lock()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Museum Ancient Objects API",
        "endpoints": {
            "GET /objects": "Get all objects",
            "GET /objects/{id}": "Get specific object",
            "POST /objects": "Create new object",
            "DELETE /objects/{id}": "Delete object",
            "PATCH /objects/{id}/status": "Update object status",
            "GET /objects/{id}/maintenance": "Get maintenance history for object",
            "POST /objects/{id}/maintenance": "Schedule maintenance task",
            "GET /maintenance/pending": "Get all pending maintenance tasks",
            "PATCH /maintenance/{record_id}/complete": "Mark maintenance as complete"
        }
    }


@app.get("/objects", response_model=List[MuseumObject])
def get_all_objects():
    """Get all museum objects"""
    return list(museum_objects.values())


@app.get("/objects/requiring-maintenance")
def get_objects_needing_maintenance():
    """Get objects that require maintenance based on rules - for agent proactive checks"""
    from datetime import datetime
    
    needs_maintenance = []
    current_date = datetime.now()
    
    for obj in museum_objects.values():
        reasons = []
        
        # Check if overdue for maintenance
        if obj.last_maintenance_date:
            last_date = datetime.strptime(obj.last_maintenance_date, "%Y-%m-%d")
            days_since = (current_date - last_date).days
            
            if days_since > obj.maintenance_interval_days:
                reasons.append(f"Overdue by {days_since - obj.maintenance_interval_days} days")
        
        # Check condition score
        if obj.condition_score < 5:
            reasons.append(f"Low condition score: {obj.condition_score}/10")
        
        # Check priority
        if obj.maintenance_priority in ["urgent", "high"]:
            reasons.append(f"Priority level: {obj.maintenance_priority}")
        
        # Check fragile items on display
        if obj.fragile and obj.status == ObjectStatus.DISPLAYED:
            reasons.append("Fragile item on public display")
        
        if reasons:
            needs_maintenance.append({
                "id": obj.id,
                "name": obj.name,
                "status": obj.status,
                "condition_score": obj.condition_score,
                "maintenance_priority": obj.maintenance_priority,
                "last_maintenance_date": obj.last_maintenance_date,
                "maintenance_interval_days": obj.maintenance_interval_days,
                "reasons": reasons
            })
    
    return {
        "count": len(needs_maintenance),
        "objects": needs_maintenance
    }


@app.get("/objects/{object_id}", response_model=MuseumObject)
def get_object(object_id: int):
    """Get a specific museum object by ID"""
    if object_id not in museum_objects:
        raise HTTPException(status_code=404, detail="Object not found")
    return museum_objects[object_id]


@app.post("/objects", response_model=MuseumObject, status_code=201)
def create_object(obj: MuseumObjectCreate):
    """Create a new museum object"""
    global next_id
    with id_lock:
        new_object = MuseumObject(
            id=next_id,
            name=obj.name,
            origin=obj.origin,
            period=obj.period,
            material=obj.material,
            description=obj.description,
            status=obj.status
        )
        museum_objects[next_id] = new_object
        next_id += 1
    return new_object


@app.delete("/objects/{object_id}", status_code=204)
def delete_object(object_id: int):
    """Delete a museum object"""
    if object_id not in museum_objects:
        raise HTTPException(status_code=404, detail="Object not found")
    del museum_objects[object_id]


@app.patch("/objects/{object_id}/status", response_model=MuseumObject)
def update_object_status(object_id: int, status_update: StatusUpdate):
    """Update the status of a museum object"""
    if object_id not in museum_objects:
        raise HTTPException(status_code=404, detail="Object not found")
    
    museum_objects[object_id].status = status_update.status
    return museum_objects[object_id]


@app.get("/objects/{object_id}/status")
def get_object_status(object_id: int):
    """Get the status of a specific museum object"""
    if object_id not in museum_objects:
        raise HTTPException(status_code=404, detail="Object not found")
    return {
        "id": object_id,
        "name": museum_objects[object_id].name,
        "status": museum_objects[object_id].status
    }


# ===== MAINTENANCE ENDPOINTS =====

@app.get("/objects/{object_id}/maintenance", response_model=List[MaintenanceRecord])
def get_object_maintenance_history(object_id: int):
    """Get maintenance history for a specific object"""
    if object_id not in museum_objects:
        raise HTTPException(status_code=404, detail="Object not found")
    
    return [record for record in maintenance_records.values() if record.object_id == object_id]


@app.post("/objects/{object_id}/maintenance", response_model=MaintenanceRecord, status_code=201)
def schedule_maintenance(object_id: int, maintenance: MaintenanceRecordCreate):
    """Schedule a maintenance task for an object"""
    global next_maintenance_id
    
    if object_id not in museum_objects:
        raise HTTPException(status_code=404, detail="Object not found")
    
    with maintenance_lock:
        new_record = MaintenanceRecord(
            id=next_maintenance_id,
            object_id=object_id,
            type=maintenance.type,
            scheduled_date=maintenance.scheduled_date,
            technician=maintenance.technician,
            notes=maintenance.notes,
            estimated_duration_hours=maintenance.estimated_duration_hours,
            cost_estimate=maintenance.cost_estimate
        )
        maintenance_records[next_maintenance_id] = new_record
        next_maintenance_id += 1
    
    return new_record


@app.get("/maintenance/pending", response_model=List[MaintenanceRecord])
def get_pending_maintenance():
    """Get all pending (not completed) maintenance tasks - used by agents for proactive monitoring"""
    return [record for record in maintenance_records.values() if not record.completed]


@app.patch("/maintenance/{record_id}/complete", response_model=MaintenanceRecord)
def complete_maintenance(record_id: int, completion: MaintenanceComplete):
    """Mark a maintenance task as complete"""
    if record_id not in maintenance_records:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    record = maintenance_records[record_id]
    if record.completed:
        raise HTTPException(status_code=400, detail="Maintenance already completed")
    
    record.completed = True
    record.completed_date = completion.completed_date or datetime.now().strftime("%Y-%m-%d")
    
    # Update the object's last maintenance date
    if record.object_id in museum_objects:
        museum_objects[record.object_id].last_maintenance_date = record.completed_date
    
    return record
