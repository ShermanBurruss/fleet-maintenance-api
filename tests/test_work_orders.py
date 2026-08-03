"""Tests for work order CRUD operations and vehicle relationships."""


def create_test_vehicle(client):
    """Create a vehicle for use in work order tests."""

    response = client.post(
        "/vehicles",
        json={
            "unit_number": "2001",
            "year": 2024,
            "manufacturer": "Freightliner",
            "model": "Cascadia",
            "status": "active",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_work_order(client):
    """A work order should be created for an existing vehicle."""

    vehicle = create_test_vehicle(client)

    response = client.post(
        "/work-orders",
        json={
            "vehicle_id": vehicle["id"],
            "description": "Replace front brake pads",
            "status": "open",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["vehicle_id"] == vehicle["id"]
    assert data["description"] == "Replace front brake pads"
    assert data["status"] == "open"
    assert data["priority"] == "high"
    assert "id" in data
    assert "created_at" in data


def test_work_order_requires_valid_vehicle(client):
    """A work order cannot reference a nonexistent vehicle."""

    response = client.post(
        "/work-orders",
        json={
            "vehicle_id": 999,
            "description": "Replace front brake pads",
            "status": "open",
            "priority": "high",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Vehicle not found"
    }


def test_get_work_order(client):
    """A created work order should be retrievable by ID."""

    vehicle = create_test_vehicle(client)

    create_response = client.post(
        "/work-orders",
        json={
            "vehicle_id": vehicle["id"],
            "description": "Annual DOT inspection",
            "status": "open",
            "priority": "normal",
        },
    )

    work_order_id = create_response.json()["id"]

    response = client.get(
        f"/work-orders/{work_order_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == work_order_id
    assert data["vehicle_id"] == vehicle["id"]
    assert data["description"] == "Annual DOT inspection"


def test_get_missing_work_order_returns_404(client):
    """Requesting a nonexistent work order should return HTTP 404."""

    response = client.get("/work-orders/999")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Work order not found"
    }


def test_update_work_order(client):
    """PATCH should update only the requested work order fields."""

    vehicle = create_test_vehicle(client)

    create_response = client.post(
        "/work-orders",
        json={
            "vehicle_id": vehicle["id"],
            "description": "Replace front brake pads",
            "status": "open",
            "priority": "high",
        },
    )

    work_order_id = create_response.json()["id"]

    response = client.patch(
        f"/work-orders/{work_order_id}",
        json={
            "status": "in_progress"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "in_progress"

    # Fields not included in the PATCH request should remain unchanged.
    assert data["vehicle_id"] == vehicle["id"]
    assert data["description"] == "Replace front brake pads"
    assert data["priority"] == "high"


def test_get_vehicle_work_orders(client):
    """Return all work orders associated with a vehicle."""

    vehicle = create_test_vehicle(client)

    client.post(
        "/work-orders",
        json={
            "vehicle_id": vehicle["id"],
            "description": "Replace brakes",
            "status": "open",
            "priority": "high",
        },
    )

    client.post(
        "/work-orders",
        json={
            "vehicle_id": vehicle["id"],
            "description": "Annual DOT inspection",
            "status": "open",
            "priority": "normal",
        },
    )

    response = client.get(
        f"/vehicles/{vehicle['id']}/work-orders"
    )

    assert response.status_code == 200

    work_orders = response.json()

    assert len(work_orders) == 2


def test_delete_work_order(client):
    """Deleting a work order should make it unavailable afterward."""

    vehicle = create_test_vehicle(client)

    create_response = client.post(
        "/work-orders",
        json={
            "vehicle_id": vehicle["id"],
            "description": "Replace air filter",
            "status": "open",
            "priority": "low",
        },
    )

    work_order_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/work-orders/{work_order_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/work-orders/{work_order_id}"
    )

    assert get_response.status_code == 404


def test_vehicle_with_work_order_cannot_be_deleted(client):
    """A vehicle with maintenance history should not be deletable."""

    vehicle = create_test_vehicle(client)

    client.post(
        "/work-orders",
        json={
            "vehicle_id": vehicle["id"],
            "description": "Replace tires",
            "status": "open",
            "priority": "high",
        },
    )

    response = client.delete(
        f"/vehicles/{vehicle['id']}"
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Vehicle cannot be deleted while "
            "work orders are associated with it."
        )
    }