"""Tests for basic API availability."""


def test_health_check(client):
    """Health endpoint should report that the API is available."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}