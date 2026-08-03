"""API routes for fleet maintenance work orders.

This module provides endpoints for creating, retrieving, updating,
and deleting maintenance work orders associated with fleet vehicles.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    WorkOrder,
    WorkOrderCreate,
    WorkOrderUpdate,
)


router = APIRouter(
    prefix="/work-orders",
    tags=["Work Orders"],
)


@router.post(
    "",
    response_model=WorkOrder,
    status_code=status.HTTP_201_CREATED,
)
def create_work_order(
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
):
    """Create a maintenance work order for an existing vehicle.

    Args:
        work_order: Validated work-order information supplied by the client.
        db: Database session provided by FastAPI dependency injection.

    Returns:
        The newly created work order.

    Raises:
        HTTPException: If the referenced vehicle does not exist.
    """

    # Verify the parent vehicle before creating a foreign-key reference.
    # This provides a clear API error instead of exposing a database error.
    vehicle = db.get(
        models.VehicleModel,
        work_order.vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    new_work_order = models.WorkOrderModel(
        vehicle_id=work_order.vehicle_id,
        description=work_order.description,
        status=work_order.status.value,
        priority=work_order.priority.value,
    )

    db.add(new_work_order)
    db.commit()

    # Reload server-generated values such as the primary-key ID and
    # creation timestamp.
    db.refresh(new_work_order)

    return new_work_order


@router.get(
    "",
    response_model=list[WorkOrder],
)
def get_work_orders(
    db: Session = Depends(get_db),
):
    """Return all maintenance work orders.

    Args:
        db: Database session provided by FastAPI dependency injection.

    Returns:
        All work orders ordered by database ID.
    """

    statement = select(
        models.WorkOrderModel
    ).order_by(
        models.WorkOrderModel.id
    )

    result = db.execute(statement)

    return result.scalars().all()


@router.get(
    "/{work_order_id}",
    response_model=WorkOrder,
)
def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
):
    """Return a specific work order by database ID.

    Args:
        work_order_id: Primary-key ID of the requested work order.
        db: Database session provided by FastAPI dependency injection.

    Returns:
        The requested work order.

    Raises:
        HTTPException: If the work order does not exist.
    """

    work_order = db.get(
        models.WorkOrderModel,
        work_order_id,
    )

    if work_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found",
        )

    return work_order


@router.patch(
    "/{work_order_id}",
    response_model=WorkOrder,
)
def update_work_order(
    work_order_id: int,
    work_order_update: WorkOrderUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an existing maintenance work order.

    Only fields explicitly supplied by the client are modified.

    Args:
        work_order_id: Primary-key ID of the work order to update.
        work_order_update: Validated fields requested for modification.
        db: Database session provided by FastAPI dependency injection.

    Returns:
        The updated work order.

    Raises:
        HTTPException: If the work order does not exist, a required field
            is explicitly set to null, or a requested vehicle does not exist.
    """

    work_order = db.get(
        models.WorkOrderModel,
        work_order_id,
    )

    if work_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found",
        )

    # Only explicitly supplied PATCH fields should be modified.
    update_data = work_order_update.model_dump(
        exclude_unset=True
    )

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

    # If the work order is being reassigned, make sure the new parent
    # vehicle exists before changing the foreign key.
    if "vehicle_id" in update_data:
        vehicle = db.get(
            models.VehicleModel,
            update_data["vehicle_id"],
        )

        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found",
            )

    for field, value in update_data.items():

        # Enum objects are converted back into the strings stored by
        # the PostgreSQL columns.
        if field in {
            "status",
            "priority",
        }:
            value = value.value

        setattr(
            work_order,
            field,
            value,
        )

    db.commit()
    db.refresh(work_order)

    return work_order


@router.delete(
    "/{work_order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
):
    """Delete an existing maintenance work order.

    Args:
        work_order_id: Primary-key ID of the work order to delete.
        db: Database session provided by FastAPI dependency injection.

    Raises:
        HTTPException: If the work order does not exist.
    """

    work_order = db.get(
        models.WorkOrderModel,
        work_order_id,
    )

    if work_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found",
        )

    db.delete(work_order)
    db.commit()