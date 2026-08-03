from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


class VehicleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class VehicleCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "unit_number": "1042",
                "year": 2022,
                "manufacturer": "Freightliner",
                "model": "Cascadia",
                "status": "active",
            }
        }
    )
    unit_number: str = Field(min_length=1, max_length=20)
    year: int = Field(ge=1980, le=datetime.now().year+1)
    manufacturer: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    status: VehicleStatus = VehicleStatus.ACTIVE

    @field_validator(
        "unit_number",
        "manufacturer",
        "model",
        mode="before",
    )
    @classmethod
    def clean_text(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        
        return value

    @field_validator("status", mode="before")
    @classmethod
    def clean_status(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

class VehicleUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "maintenance"
            }
        }
    )

    unit_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    year: int | None = Field(
        default=None,
        ge=1980,
        le=datetime.now().year + 1,
    )

    manufacturer: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    status: VehicleStatus | None = None

    @field_validator(
        "unit_number",
        "manufacturer",
        "model",
        mode="before",
    )
    @classmethod
    def clean_text(cls, value):
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("status", mode="before")
    @classmethod
    def clean_status(cls, value):
        if isinstance(value, str):
            return value.strip().lower()

        return value
    
class Vehicle(VehicleCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

class WorkOrderStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrderPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class WorkOrderCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicle_id": 1,
                "description": "Replace front brake pads",
                "status": "open",
                "priority": "high",
            }
        }
    )

    vehicle_id: int = Field(gt=0)

    description: str = Field(
        min_length=3,
        max_length=500,
    )

    status: WorkOrderStatus = WorkOrderStatus.OPEN
    priority: WorkOrderPriority = WorkOrderPriority.NORMAL

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value):
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("status", "priority", mode="before")
    @classmethod
    def clean_enum_values(cls, value):
        if isinstance(value, str):
            return value.strip().lower()

        return value


class WorkOrderUpdate(BaseModel):
    vehicle_id: int | None = Field(
        default=None,
        gt=0,
    )

    description: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )

    status: WorkOrderStatus | None = None
    priority: WorkOrderPriority | None = None

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value):
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("status", "priority", mode="before")
    @classmethod
    def clean_enum_values(cls, value):
        if isinstance(value, str):
            return value.strip().lower()

        return value


class WorkOrder(WorkOrderCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime