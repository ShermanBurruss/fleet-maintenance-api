"""Application entry point for the Fleet Maintenance API.

This module creates and configures the FastAPI application and registers
the application's feature-specific API routers.

Database schema changes are managed through Alembic migrations rather
than being created automatically during application startup.
"""

from fastapi import FastAPI

from app.routers import vehicles, work_orders


app = FastAPI(
    title="Fleet Maintenance API",
    description=(
        "A portfolio REST API for managing fleet vehicles "
        "and maintenance work orders."
    ),
    version="0.1.0",
)


# Register feature-specific route modules with the main application.
app.include_router(vehicles.router)
app.include_router(work_orders.router)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    """Return a message confirming that the API is running."""

    return {
        "message": "Fleet Maintenance API is running"
    }


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Return the current basic health status of the API."""

    return {
        "status": "ok"
    }