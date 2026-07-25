# Basic API Example

A simple REST API with CRUD operations.

## Setup

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

## Endpoints

- `GET /items` - List items
- `POST /items` - Create item
- `GET /items/{id}` - Get item
- `PUT /items/{id}` - Update item
- `DELETE /items/{id}` - Delete item
