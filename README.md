# Fleet Maintenance API

[![CI](https://github.com/ShermanBurruss/fleet-maintenance-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ShermanBurruss/fleet-maintenance-api/actions/workflows/ci.yml)

A RESTful backend API for managing fleet vehicles and maintenance work orders.

This project was built as a backend development portfolio project using FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker, Pydantic, and Pytest. It demonstrates practical API design, relational database modeling, validation, database migrations, automated testing, and environment-based configuration.

---

## Features

- Create, retrieve, update, and delete fleet vehicles
- Create, retrieve, update, and delete maintenance work orders
- Associate multiple work orders with a single vehicle
- Prevent work orders from referencing nonexistent vehicles
- Prevent deletion of vehicles that still have associated maintenance history
- Partial updates using HTTP PATCH
- Request and response validation using Pydantic
- PostgreSQL persistence using SQLAlchemy ORM
- Database schema management using Alembic migrations
- Environment-based database configuration
- Separate development and automated-test databases
- Automated API testing using Pytest and FastAPI TestClient
- Modular API routing for easier maintenance and expansion
- Automatically generated OpenAPI and Swagger documentation

---

## Technology Stack

### Backend

- Python 3.10
- FastAPI
- Pydantic
- Pydantic Settings
- SQLAlchemy

### Database

- PostgreSQL 17
- Psycopg
- Alembic

### Testing

- Pytest
- FastAPI TestClient
- HTTPX

### Development Environment

- Docker
- Visual Studio Code
- PowerShell
- Git

---

## Project Structure

```text
fleet-maintenance-api-starter/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── vehicles.py
│   │   └── work_orders.py
│   │
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_vehicles.py
│   └── test_work_orders.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## Database Design

The API currently uses two primary tables.

### Vehicles

Each vehicle represents a fleet asset.

Fields include:

- `id`
- `unit_number`
- `year`
- `manufacturer`
- `model`
- `status`

Vehicle unit numbers must be unique.

### Work Orders

Each work order represents a maintenance task associated with a vehicle.

Fields include:

- `id`
- `vehicle_id`
- `description`
- `status`
- `priority`
- `created_at`

`vehicle_id` is a foreign key referencing the `vehicles` table.

A vehicle can have multiple work orders:

```text
Vehicle
   │
   ├── Work Order
   ├── Work Order
   └── Work Order
```

Vehicles cannot be deleted while work orders still reference them. This protects maintenance history from becoming orphaned.

---

## Vehicle Status Values

Vehicles currently support the following status values:

```text
active
inactive
maintenance
out_of_service
```

---

## Work Order Status Values

Work orders currently support:

```text
open
in_progress
completed
cancelled
```

---

## Work Order Priority Values

Work order priorities include:

```text
low
normal
high
critical
```

---

## API Endpoints

### System

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Confirm that the API is running |
| GET | `/health` | Basic API health check |

### Vehicles

| Method | Endpoint | Description |
|---|---|---|
| POST | `/vehicles` | Create a vehicle |
| GET | `/vehicles` | Retrieve all vehicles |
| GET | `/vehicles/{vehicle_id}` | Retrieve one vehicle |
| PATCH | `/vehicles/{vehicle_id}` | Partially update a vehicle |
| DELETE | `/vehicles/{vehicle_id}` | Delete a vehicle |
| GET | `/vehicles/{vehicle_id}/work-orders` | Retrieve all work orders for a vehicle |

### Work Orders

| Method | Endpoint | Description |
|---|---|---|
| POST | `/work-orders` | Create a work order |
| GET | `/work-orders` | Retrieve all work orders |
| GET | `/work-orders/{work_order_id}` | Retrieve one work order |
| PATCH | `/work-orders/{work_order_id}` | Partially update a work order |
| DELETE | `/work-orders/{work_order_id}` | Delete a work order |

---

## Example Vehicle Request

### Create Vehicle

```http
POST /vehicles
```

```json
{
  "unit_number": "1042",
  "year": 2022,
  "manufacturer": "Freightliner",
  "model": "Cascadia",
  "status": "active"
}
```

Example response:

```json
{
  "unit_number": "1042",
  "year": 2022,
  "manufacturer": "Freightliner",
  "model": "Cascadia",
  "status": "active",
  "id": 1
}
```

---

## Example Work Order Request

### Create Work Order

```http
POST /work-orders
```

```json
{
  "vehicle_id": 1,
  "description": "Replace front brake pads",
  "status": "open",
  "priority": "high"
}
```

Example response:

```json
{
  "vehicle_id": 1,
  "description": "Replace front brake pads",
  "status": "open",
  "priority": "high",
  "id": 1,
  "created_at": "2026-08-02T18:30:00Z"
}
```

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd fleet-maintenance-api-starter
```

### 2. Create a Python virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## PostgreSQL Development Database

The project expects PostgreSQL to be available locally.

One option is to run PostgreSQL using Docker:

```powershell
docker run `
  --name fleet-postgres `
  -e POSTGRES_USER=fleetuser `
  -e POSTGRES_PASSWORD=fleetpass `
  -e POSTGRES_DB=fleetdb `
  -p 5432:5432 `
  -v fleet-postgres-data:/var/lib/postgresql/data `
  -d postgres:17
```

The credentials shown above are example local-development credentials only.

---

## Environment Configuration

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure the appropriate database URLs.

Example:

```text
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/fleetdb
TEST_DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/fleetdb_test
```

The `.env` file is intentionally excluded from Git and should never contain credentials that are committed to the repository.

---

## Database Migrations

Database schema changes are managed through Alembic.

Apply all migrations:

```powershell
alembic upgrade head
```

View the current migration:

```powershell
alembic current
```

View migration history:

```powershell
alembic history
```

Generate a migration after changing SQLAlchemy models:

```powershell
alembic revision --autogenerate -m "describe schema change"
```

Generated migrations should always be reviewed before being applied.

---

## Running the API

Start the FastAPI development server:

```powershell
fastapi dev app/main.py
```

The application will typically be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## Automated Testing

The project uses Pytest and a dedicated PostgreSQL test database.

Run all tests:

```powershell
pytest
```

Run tests with detailed output:

```powershell
pytest -v
```

Current automated coverage includes:

- API health checks
- Vehicle creation
- Duplicate vehicle validation
- Vehicle retrieval
- Missing-vehicle handling
- Vehicle partial updates
- Duplicate unit-number updates
- Vehicle deletion
- Work order creation
- Invalid vehicle references
- Work order retrieval
- Missing-work-order handling
- Work order partial updates
- Vehicle/work-order relationship queries
- Work order deletion
- Prevention of vehicle deletion while maintenance history exists

The current test suite contains 16 passing automated API tests.

---

## Validation and Error Handling

The API uses Pydantic to validate incoming request data.

Examples include:

- Vehicle unit numbers cannot be empty
- Vehicle status must use an allowed value
- Work order priority must use an allowed value
- Work order descriptions must meet minimum-length requirements
- Work orders cannot reference nonexistent vehicles
- Required fields cannot explicitly be set to `null` through PATCH requests
- Duplicate vehicle unit numbers return HTTP `409 Conflict`
- Missing resources return HTTP `404 Not Found`

Database transactions are rolled back when integrity constraints fail so that database sessions remain usable.

---

## API Organization

Routes are separated by responsibility using FastAPI's `APIRouter`.

```text
main.py
   │
   ├── System
   │
   ├── Vehicles Router
   │
   └── Work Orders Router
```

This keeps the application entry point small while allowing individual areas of the API to grow independently.

---

## Development Practices Demonstrated

This project demonstrates several backend-development practices beyond basic CRUD operations:

- RESTful route design
- Relational database modeling
- Foreign-key integrity
- SQLAlchemy ORM usage
- Pydantic validation
- Dependency injection
- Transaction management
- HTTP status-code handling
- Partial resource updates
- Automated integration testing
- Isolated test databases
- Database migration management
- Environment-based configuration
- Separation of application concerns
- In-code documentation and docstrings
- Git-safe handling of credentials

---

## Future Improvements

Planned or potential additions include:

- Expanded vehicle maintenance history
- Service dates and odometer readings
- Technician assignments
- Work order notes and comments
- Cost tracking
- Parts and service records
- Vehicle-detailing records
- Pagination and filtering
- API authentication and authorization
- Additional Pytest coverage
- Test coverage reporting
- Docker Compose configuration
- CI testing through GitHub Actions
- Deployment to a cloud platform
- Additional production logging and monitoring

---

## Project Purpose

This project was created to strengthen practical backend-development skills through a real-world fleet-maintenance use case.

The goal is to demonstrate the ability to design, build, organize, test, and maintain a relational REST API using technologies commonly found in modern Python backend development.
