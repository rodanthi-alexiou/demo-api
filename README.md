# Museum Ancient Objects API

A FastAPI-based REST API for managing museum artifacts, designed for deployment to Azure Web Apps.

## Overview

This API provides endpoints to manage a collection of ancient world objects in a museum setting. It includes 10 pre-populated ancient artifacts with fields such as name, origin, period, material, and description. Each object has a status that can be tracked and updated.

**New Maintenance Features**: The API now includes comprehensive maintenance tracking capabilities designed for multi-agent workflows. Agents can proactively monitor object conditions, schedule maintenance tasks, and track completion status. Each object includes maintenance metadata such as condition scores, maintenance intervals, and priority levels.

## Object Status

Objects can have one of three statuses:
- `displayed` - Currently on display in the museum
- `in-restoration` - Being restored
- `to-other-museum` - Loaned to another museum

## Maintenance System

The API includes a comprehensive maintenance tracking system with the following features:

### Maintenance Priority Levels
- `low` - Routine maintenance
- `normal` - Standard maintenance schedule
- `high` - Elevated priority (high-traffic items, fragile objects)
- `urgent` - Immediate attention required

### Maintenance Types
- `cleaning` - Regular cleaning procedures
- `restoration` - Repair and restoration work
- `inspection` - Condition assessment
- `preventive` - Preventive maintenance

### Environmental Sensitivity
- `low` - Robust materials (stone, metal)
- `normal` - Standard sensitivity
- `high` - Sensitive to light, humidity, temperature (parchment, textiles)

### Proactive Monitoring
Agents can query `/objects/requiring-maintenance` and `/maintenance/pending` to identify objects that need attention based on:
- Overdue maintenance (last maintenance date + interval)
- Low condition scores (< 5/10)
- High/urgent priority items
- Fragile items on public display

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. Run the application (locally):
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Root
- **GET /** - API information and available endpoints

### Objects
- **GET /objects** - Get all museum objects
- **GET /objects/{id}** - Get a specific object by ID
- **POST /objects** - Create a new museum object
- **DELETE /objects/{id}** - Delete an object by ID

### Status
- **GET /objects/{id}/status** - Get the status of a specific object
- **PATCH /objects/{id}/status** - Update the status of an object

### Maintenance
- **GET /objects/{id}/maintenance** - Get maintenance history for a specific object
- **POST /objects/{id}/maintenance** - Schedule a new maintenance task for an object
- **GET /maintenance/pending** - Get all pending (incomplete) maintenance tasks
- **PATCH /maintenance/{record_id}/complete** - Mark a maintenance task as complete
- **GET /objects/requiring-maintenance** - Get objects that need maintenance (agent endpoint)

## Example Objects

The API comes pre-populated with 10 ancient world objects:

1. Rosetta Stone (Egypt, 196 BC)
2. Venus de Milo (Greece, 130-100 BC)
3. Terracotta Army Warrior (China, 210-209 BC)
4. Code of Hammurabi (Babylon, 1754 BC)
5. Dead Sea Scrolls Fragment (Israel, 300 BC - 100 AD)
6. Mask of Agamemnon (Greece, 1600-1500 BC)
7. Parthenon Frieze (Greece, 447-438 BC)
8. Nefertiti Bust (Egypt, 1345 BC)
9. Sumerian Cuneiform Tablet (Mesopotamia, 3200 BC)
10. Olmec Colossal Head (Mexico, 1500-1000 BC)

## API Usage Examples

### Get all objects
```bash
curl http://localhost:8000/objects
```

### Get a specific object
```bash
curl http://localhost:8000/objects/1
```

### Create a new object
```bash
curl -X POST http://localhost:8000/objects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Persian Cylinder Seal",
    "origin": "Persia",
    "period": "500 BC",
    "material": "Lapis Lazuli",
    "description": "Ancient Persian administrative seal",
    "status": "displayed"
  }'
```

### Update object status
```bash
curl -X PATCH http://localhost:8000/objects/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "in-restoration"}'
```

### Get object status
```bash
curl http://localhost:8000/objects/1/status
```

### Delete an object
```bash
curl -X DELETE http://localhost:8000/objects/1
```

### Schedule maintenance
```bash
curl -X POST http://localhost:8000/objects/5/maintenance \
  -H "Content-Type: application/json" \
  -d '{
    "type": "inspection",
    "scheduled_date": "2026-03-15",
    "technician": "Dr. Sarah Chen",
    "notes": "Urgent inspection for Dead Sea Scrolls",
    "estimated_duration_hours": 3,
    "cost_estimate": 500.0
  }'
```

### Get pending maintenance tasks
```bash
curl http://localhost:8000/maintenance/pending
```

### Complete a maintenance task
```bash
curl -X PATCH http://localhost:8000/maintenance/1/complete \
  -H "Content-Type: application/json" \
  -d '{"completed_date": "2026-03-02"}'
```

### Get maintenance history for an object
```bash
curl http://localhost:8000/objects/5/maintenance
```

### Get objects requiring maintenance (for agent monitoring)
```bash
curl http://localhost:8000/objects/requiring-maintenance
```

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Azure Deployment

This API is designed to be deployed to Azure Web Apps. The `requirements.txt` file includes all necessary dependencies for deployment.

### Deployment Steps
1. Create an Azure Web App with Python runtime
2. Deploy the code to Azure
3. Azure will automatically install dependencies from `requirements.txt`
4. The application will start using the default command: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Data Model

### MuseumObject
```json
{
  "id": 1,
  "name": "Rosetta Stone",
  "origin": "Egypt",
  "period": "196 BC",
  "material": "Granodiorite",
  "description": "Ancient Egyptian decree inscribed in three scripts",
  "status": "displayed",
  "last_maintenance_date": "2025-09-15",
  "maintenance_interval_days": 60,
  "condition_score": 7,
  "maintenance_priority": "high",
  "fragile": false,
  "environmental_sensitivity": "normal"
}
```

### MaintenanceRecord
```json
{
  "id": 1,
  "object_id": 5,
  "type": "inspection",
  "scheduled_date": "2026-03-15",
  "technician": "Dr. Sarah Chen",
  "notes": "Urgent inspection for Dead Sea Scrolls",
  "completed": false,
  "completed_date": null,
  "estimated_duration_hours": 3,
  "cost_estimate": 500.0
}
```

## Multi-Agent Workflow Integration

This API is designed to work seamlessly with multi-agent systems for proactive museum management:

### Agent Workflow Example
1. **Monitoring Agent** periodically calls `/objects/requiring-maintenance` to identify items needing attention
2. **Scheduling Agent** creates maintenance tasks via `POST /objects/{id}/maintenance`
3. **Execution Agent** retrieves pending tasks from `/maintenance/pending`
4. **Completion Agent** marks tasks complete via `PATCH /maintenance/{record_id}/complete`
5. System automatically updates `last_maintenance_date` when maintenance is completed

### Detection Logic
The API automatically flags objects requiring maintenance when:
- Days since last maintenance > maintenance interval
- Condition score < 5/10
- Priority level is "high" or "urgent"
- Fragile items are on public display

### Sample Multi-Agent Response
When an agent queries `/objects/requiring-maintenance`, it receives:
```json
{
  "count": 8,
  "objects": [
    {
      "id": 5,
      "name": "Dead Sea Scrolls Fragment",
      "status": "in-restoration",
      "condition_score": 4,
      "maintenance_priority": "urgent",
      "last_maintenance_date": "2026-01-05",
      "maintenance_interval_days": 30,
      "reasons": [
        "Overdue by 26 days",
        "Low condition score: 4/10",
        "Priority level: urgent"
      ]
    }
  ]
}
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running the application
