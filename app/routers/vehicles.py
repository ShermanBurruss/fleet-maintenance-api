"""API routes for fleet vehicle operations.

This module provides endpoints for creating, retrieving, updating, and
deleting fleet vehicles. It also exposes vehicle-specific maintenance
work-order relationships.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    Vehicle,
    VehicleCreate,
    VehicleUpdate,
    WorkOrder,
)


router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"],
)


@router.post(
    "",
    response_model=Vehicle,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
):
    """Create a new vehicle in the fleet.

    Args:
        vehicle: Validated vehicle information supplied by the client.
        db: Database session provided by FastAPI dependency injection.

    Returns:
        The newly created vehicle.

    Raises:
        HTTPException: If another vehicle already uses the supplied
            unit number.
    """

    # Convert the validated API request into a SQLAlchemy database model.
    new_vehicle = models.VehicleModel(
        unit_number=vehicle.unit_number,
        year=vehicle.year,
        manufacturer=vehicle.manufacturer,
        model=vehicle.model,
        status=vehicle.status.value,
    )

    db.add(new_vehicle)

    try:
        db.commit()

    except IntegrityError as exc:
        # unit_number has a UNIQUE database constraint. The failed
        # transaction must be rolled back before the session can be reused.
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A vehicle with this unit number already exists",
        ) from exc

    # Refresh the object so database-generated values, such as its ID,
    # are available before returning the response.
    db.refresh(new_vehicle)

    return new_vehicle


@router.get(
    "",
    response_model=list[Vehicle],
)
def get_vehicles(
    db: Session = Depends(get_db),
):
    """Return all vehicles currently stored in the fleet database.

    Args:
        db: Database session provided by FastAPI dependency injection.

    Returns:
        A list containing all fleet vehicles.
    """

    statement = select(
        models.VehicleModel
    ).order_by(
        models.VehicleModel.id
    )

    result = db.execute(statement)

    return result.scalars().all()


@router.get(
    "/{vehicle_id}",
    response_model=Vehicle,
)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """Return a specific vehicle by database ID.

    Args:
        vehicle_id: Primary-key ID of the requested vehicle.
        db: Database session provided by FastAPI dependency injection.

    Returns:
        The requested vehicle.

    Raises:
        HTTPException: If no vehicle exists with the supplied ID.
    """

    vehicle = db.get(
        models.VehicleModel,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    return vehicle


@router.patch(
    "/{vehicle_id}",
    response_model=Vehicle,
)
def update_vehicle(
    vehicle_id: int,
    vehicle_update: VehicleUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an existing vehicle.

    Only fields explicitly supplied by the client are modified.

    Args:
        vehicle_id: Primary-key ID of the vehicle to update.
        vehicle_update: Validated fields requested for modification.
        db: Database session provided by FastAPI dependency injection.

    Returns:
        The updated vehicle.

    Raises:
        HTTPException: If the vehicle does not exist, a required field
            is explicitly set to null, or the new unit number conflicts
            with another vehicle.
    """

    vehicle = db.get(
        models.VehicleModel,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    # exclude_unset=True distinguishes omitted PATCH fields from fields
    # that the client intentionally supplied.
    update_data = vehicle_update.model_dump(
        exclude_unset=True
    )

    # Required database fields may be omitted from a PATCH request,
    # but they cannot explicitly be changed to null.
    if any(
        value is None
        for value in update_data.values()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Fields cannot be null. "
                "Omit fields you do not want to change."
            ),
        )

    for field, value in update_data.items():

        # Pydantic represents status as an Enum. PostgreSQL currently
        # stores the Enum's underlying string value.
        if field == "status":
            value = value.value

        setattr(
            vehicle,
            field,
            value,
        )

    try:
        db.commit()

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A vehicle with this unit number already exists",
        ) from exc

    db.refresh(vehicle)

    return vehicle


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """Delete a vehicle that has no associated work orders.

    Args:
        vehicle_id: Primary-key ID of the vehicle to delete.
        db: Database session provided by FastAPI dependency injection.

    Raises:
        HTTPException: If the vehicle does not exist or work orders
            still reference it.
    """

    vehicle = db.get(
        models.VehicleModel,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    db.delete(vehicle)

    try:
        db.commit()

    except IntegrityError as exc:
        # The work_orders foreign key protects maintenance history from
        # being orphaned when a vehicle is deleted.
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Vehicle cannot be deleted while "
                "work orders are associated with it."
            ),
        ) from exc


@router.get(
    "/{vehicle_id}/work-orders",
    response_model=list[WorkOrder],
)
def get_vehicle_work_orders(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """Return all maintenance work orders belonging to a vehicle.

    Args:
        vehicle_id: Primary-key ID of the requested vehicle.
        db: Database session provided by FastAPI dependency injection.

    Returns:
        All work orders associated with the requested vehicle.

    Raises:
        HTTPException: If the vehicle does not exist.
    """

    # Validate the parent vehicle first so a nonexistent vehicle produces
    # a 404 rather than an indistinguishable empty work-order list.
    vehicle = db.get(
        models.VehicleModel,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    statement = (
        select(models.WorkOrderModel)
        .where(
            models.WorkOrderModel.vehicle_id
            == vehicle_id
        )
        .order_by(
            models.WorkOrderModel.id
        )
    )

    result = db.execute(statement)

    return result.scalars().all()