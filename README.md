# Museum Ancient Objects API

A FastAPI-based REST API for managing museum artifacts, designed for deployment to Azure Web Apps.

## Overview

This API provides endpoints to manage a collection of ancient world objects in a museum setting. It includes 10 pre-populated ancient artifacts with fields such as name, origin, period, material, and description. Each object has a status that can be tracked and updated.

## Object Status

Objects can have one of three statuses:
- `displayed` - Currently on display in the museum
- `in-restoration` - Being restored
- `to-other-museum` - Loaned to another museum

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
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
  "status": "displayed"
}
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running the application
