# Fleet Maintenance API

[![CI](https://github.com/ShermanBurruss/fleet-maintenance-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ShermanBurruss/fleet-maintenance-api/actions/workflows/ci.yml)

A RESTful backend API for managing fleet vehicles and maintenance work orders.

This project was built as a backend development portfolio project using FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker, Docker Compose, Pydantic, Pytest, and GitHub Actions. It demonstrates practical API design, relational database modeling, validation, database migrations, automated testing, environment-based configuration, containerization, and continuous integration.

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
- Dockerized FastAPI application
- Multi-container local development with Docker Compose
- PostgreSQL health checks and automatic migration application at container startup
- Continuous integration through GitHub Actions

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

### Containerization and CI

- Docker
- Docker Compose
- GitHub Actions

### Development Environment

- Visual Studio Code
- PowerShell
- Git
- GitHub

---

## Project Structure

```text
fleet-maintenance-api/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── alembic/
│   ├── versions/
│   │   └── ce7e86ebd67b_create_initial_schema.py
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
├── docker/
│   └── postgres/
│       └── init-test-db.sql
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_vehicles.py
│   └── test_work_orders.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── compose.yaml
├── Dockerfile
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

# Docker Compose Quick Start

The recommended way to run the Fleet Maintenance API locally is with Docker Compose.

Docker Compose starts both PostgreSQL 17 and the FastAPI application. The API waits for PostgreSQL to become healthy, applies pending Alembic migrations, and then starts the web server.

## Prerequisites

Install:

- Git
- Docker Desktop

Python and PostgreSQL do not need to be installed directly on the host machine when using Docker Compose.

## 1. Clone the Repository

```bash
git clone https://github.com/ShermanBurruss/fleet-maintenance-api.git
cd fleet-maintenance-api
```

## 2. Build the Application Image

```bash
docker compose build
```

## 3. Start the Stack

Run in the foreground:

```bash
docker compose up
```

Or run in detached mode:

```bash
docker compose up -d
```

Docker Compose will:

1. Start PostgreSQL 17
2. Create the development database
3. Create the dedicated test database when the PostgreSQL volume is first initialized
4. Wait for PostgreSQL to pass its health check
5. Run `alembic upgrade head`
6. Start the FastAPI application

## 4. Open the API

Application root:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

## 5. Check Container Status

```bash
docker compose ps
```

## 6. View Logs

View the entire stack:

```bash
docker compose logs
```

View only API logs:

```bash
docker compose logs api
```

Follow API logs continuously:

```bash
docker compose logs -f api
```

## 7. Stop the Stack

```bash
docker compose down
```

This removes the running containers and Compose network while preserving PostgreSQL data.

To completely reset the Compose databases:

```bash
docker compose down -v
```

> **Warning:** `docker compose down -v` permanently deletes the PostgreSQL data volume created by Docker Compose.

---

## Docker Compose Architecture

```text
Browser
   │
   │ localhost:8000
   ▼
FastAPI Container
   │
   │ Docker internal network
   │ db:5432
   ▼
PostgreSQL 17 Container
```

Inside Docker Compose, the FastAPI service connects to PostgreSQL using the service name `db` instead of `localhost`.

Environment-based configuration allows the same Python source code to run both directly on the host and inside containers without changing application code.

---

# Manual Local Development

The API can also run directly from Python on the host machine.

This workflow is useful for active development, debugging, and running the automated test suite.

## 1. Create a Python Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

## 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 3. Make PostgreSQL Available

PostgreSQL must be reachable on port `5432`.

You can use the PostgreSQL service from Docker Compose, or run a standalone development container:

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

The credentials shown above are local-development examples only.
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

The initial migration creates the `vehicles` and `work_orders` tables, the foreign-key relationship between them, the work-order vehicle lookup index, and Alembic's schema-version tracking.

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

## Continuous Integration

The repository includes a GitHub Actions workflow at:

```text
.github/workflows/ci.yml
```

The workflow runs automatically when code is pushed to `main` or when a pull request targets `main`.

The CI pipeline:

1. Starts a temporary PostgreSQL 17 service
2. Checks out the repository
3. Configures Python
4. Installs dependencies from `requirements.txt`
5. Runs `alembic upgrade head`
6. Runs the complete Pytest suite

This verifies both application behavior and the ability of Alembic migrations to build the schema from an empty PostgreSQL database.

The CI status badge at the top of this README reflects the current GitHub Actions result.

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
- Docker image creation
- Multi-container local development with Docker Compose
- PostgreSQL container health checks
- Automatic migration application during container startup
- GitHub Actions continuous integration
- Automated CI database provisioning

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
- Search and sorting
- API authentication and authorization
- User roles and permissions
- Additional Pytest coverage
- Test coverage reporting
- Production logging
- Structured application monitoring
- Cloud deployment
- Production PostgreSQL hosting
- HTTPS and custom-domain configuration
- Automated deployment after successful CI
- Additional GitHub Actions quality checks
---

## Project Purpose

This project was created to strengthen practical backend-development skills through a real-world fleet-maintenance use case.

The goal is to demonstrate the ability to design, build, organize, test, containerize, and maintain a relational REST API using technologies commonly found in modern Python backend development.

The project is intentionally being expanded in stages so each new capability introduces a practical backend-development concept while preserving automated test coverage and documented project history.
