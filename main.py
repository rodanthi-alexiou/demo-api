from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

app = FastAPI(title="Museum Ancient Objects API")


class ObjectStatus(str, Enum):
    """Status of museum objects"""
    DISPLAYED = "displayed"
    IN_RESTORATION = "in-restoration"
    TO_OTHER_MUSEUM = "to-other-museum"


class MuseumObject(BaseModel):
    """Model for museum objects"""
    id: int
    name: str
    origin: str
    period: str
    material: str
    description: str
    status: ObjectStatus = ObjectStatus.DISPLAYED


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


# In-memory storage with 10 ancient world objects
museum_objects = {
    1: MuseumObject(
        id=1,
        name="Rosetta Stone",
        origin="Egypt",
        period="196 BC",
        material="Granodiorite",
        description="Ancient Egyptian decree inscribed in three scripts",
        status=ObjectStatus.DISPLAYED
    ),
    2: MuseumObject(
        id=2,
        name="Venus de Milo",
        origin="Greece",
        period="130-100 BC",
        material="Marble",
        description="Ancient Greek statue of Aphrodite",
        status=ObjectStatus.DISPLAYED
    ),
    3: MuseumObject(
        id=3,
        name="Terracotta Army Warrior",
        origin="China",
        period="210-209 BC",
        material="Terracotta",
        description="Life-sized warrior from Emperor Qin's tomb",
        status=ObjectStatus.IN_RESTORATION
    ),
    4: MuseumObject(
        id=4,
        name="Code of Hammurabi",
        origin="Babylon",
        period="1754 BC",
        material="Basalt",
        description="Ancient Babylonian law code",
        status=ObjectStatus.DISPLAYED
    ),
    5: MuseumObject(
        id=5,
        name="Dead Sea Scrolls Fragment",
        origin="Israel",
        period="300 BC - 100 AD",
        material="Parchment",
        description="Ancient Jewish religious manuscript",
        status=ObjectStatus.IN_RESTORATION
    ),
    6: MuseumObject(
        id=6,
        name="Mask of Agamemnon",
        origin="Greece",
        period="1600-1500 BC",
        material="Gold",
        description="Mycenaean funeral mask",
        status=ObjectStatus.DISPLAYED
    ),
    7: MuseumObject(
        id=7,
        name="Parthenon Frieze",
        origin="Greece",
        period="447-438 BC",
        material="Marble",
        description="Classical Greek sculptural decoration",
        status=ObjectStatus.TO_OTHER_MUSEUM
    ),
    8: MuseumObject(
        id=8,
        name="Nefertiti Bust",
        origin="Egypt",
        period="1345 BC",
        material="Limestone",
        description="Portrait of Egyptian Queen Nefertiti",
        status=ObjectStatus.DISPLAYED
    ),
    9: MuseumObject(
        id=9,
        name="Sumerian Cuneiform Tablet",
        origin="Mesopotamia",
        period="3200 BC",
        material="Clay",
        description="Early writing system example",
        status=ObjectStatus.IN_RESTORATION
    ),
    10: MuseumObject(
        id=10,
        name="Olmec Colossal Head",
        origin="Mexico",
        period="1500-1000 BC",
        material="Basalt",
        description="Massive stone head sculpture",
        status=ObjectStatus.DISPLAYED
    )
}

# Counter for generating new IDs
next_id = 11


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
            "PATCH /objects/{id}/status": "Update object status"
        }
    }


@app.get("/objects", response_model=List[MuseumObject])
def get_all_objects():
    """Get all museum objects"""
    return list(museum_objects.values())


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
    return None


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
