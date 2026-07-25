# ERP System Example

A complete enterprise resource planning system.

## Features

- User management with RBAC
- Inventory management
- Order processing
- Financial reporting
- Dashboard with analytics

## Setup

```bash
superdev init my-erp --example erp-system
cd my-erp
superdev dev
```

## Architecture

- **Backend**: FastAPI with SQLAlchemy
- **Frontend**: React + Tailwind
- **Database**: PostgreSQL
- **Cache**: Redis

## API Endpoints

- `POST /api/v1/auth/login` - Authentication
- `GET /api/v1/users` - User management
- `GET /api/v1/inventory` - Inventory
- `POST /api/v1/orders` - Orders
- `GET /api/v1/reports/financial` - Financial reports
