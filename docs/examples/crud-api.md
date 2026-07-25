# CRUD API Example

A basic REST API with Create, Read, Update, Delete operations.

## Setup

```bash
superdev init my-api --template fastapi
cd my-api
superdev dev
```

## Endpoints

```bash
# Create
curl -X POST http://localhost:8000/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Item 1", "description": "A test item"}'

# Read
curl http://localhost:8000/api/v1/items
curl http://localhost:8000/api/v1/items/1

# Update
curl -X PUT http://localhost:8000/api/v1/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item"}'

# Delete
curl -X DELETE http://localhost:8000/api/v1/items/1
```
