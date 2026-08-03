"""Tests for vehicle CRUD operations."""


def test_create_vehicle(client):
    """A valid vehicle should be created successfully."""

    vehicle_data = {
        "unit_number": "1042",
        "year": 2022,
        "manufacturer": "Freightliner",
        "model": "Cascadia",
        "status": "active",
    }

    response = client.post(
        "/vehicles",
        json=vehicle_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["unit_number"] == "1042"
    assert data["year"] == 2022
    assert data["manufacturer"] == "Freightliner"
    assert data["model"] == "Cascadia"
    assert data["status"] == "active"
    assert "id" in data


def test_duplicate_unit_number_returns_conflict(client):
    """Duplicate vehicle unit numbers should return HTTP 409."""

    vehicle_data = {
        "unit_number": "1042",
        "year": 2022,
        "manufacturer": "Freightliner",
        "model": "Cascadia",
        "status": "active",
    }

    first_response = client.post(
        "/vehicles",
        json=vehicle_data,
    )

    second_response = client.post(
        "/vehicles",
        json=vehicle_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "A vehicle with this unit number already exists"
    }

def test_get_vehicle(client):
    """A created vehicle should be retrievable by ID."""

    create_response = client.post(
        "/vehicles",
        json={
            "unit_number": "1075",
            "year": 2023,
            "manufacturer": "Peterbilt",
            "model": "579",
            "status": "active",
        },
    )

    vehicle_id = create_response.json()["id"]

    response = client.get(
        f"/vehicles/{vehicle_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == vehicle_id
    assert data["unit_number"] == "1075"


def test_get_missing_vehicle_returns_404(client):
    """Requesting a nonexistent vehicle should return HTTP 404."""

    response = client.get("/vehicles/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Vehicle not found"
    }


def test_update_vehicle_status(client):
    """PATCH should update only the requested vehicle fields."""

    create_response = client.post(
        "/vehicles",
        json={
            "unit_number": "1100",
            "year": 2024,
            "manufacturer": "Freightliner",
            "model": "Cascadia",
            "status": "active",
        },
    )

    vehicle_id = create_response.json()["id"]

    response = client.patch(
        f"/vehicles/{vehicle_id}",
        json={
            "status": "maintenance"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "maintenance"

    # Values not included in the PATCH request must remain unchanged.
    assert data["unit_number"] == "1100"
    assert data["manufacturer"] == "Freightliner"
    assert data["model"] == "Cascadia"


def test_update_vehicle_duplicate_unit_returns_conflict(client):
    """A vehicle cannot be updated to another vehicle's unit number."""

    first_vehicle = client.post(
        "/vehicles",
        json={
            "unit_number": "1200",
            "year": 2024,
            "manufacturer": "Kenworth",
            "model": "T680",
            "status": "active",
        },
    )

    second_vehicle = client.post(
        "/vehicles",
        json={
            "unit_number": "1201",
            "year": 2024,
            "manufacturer": "Peterbilt",
            "model": "579",
            "status": "active",
        },
    )

    second_vehicle_id = second_vehicle.json()["id"]

    response = client.patch(
        f"/vehicles/{second_vehicle_id}",
        json={
            "unit_number": first_vehicle.json()["unit_number"]
        },
    )

    assert response.status_code == 409


def test_delete_vehicle(client):
    """Deleting a vehicle should make it unavailable afterward."""

    create_response = client.post(
        "/vehicles",
        json={
            "unit_number": "1300",
            "year": 2024,
            "manufacturer": "Kenworth",
            "model": "T680",
            "status": "active",
        },
    )

    vehicle_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/vehicles/{vehicle_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/vehicles/{vehicle_id}"
    )

    assert get_response.status_code == 404