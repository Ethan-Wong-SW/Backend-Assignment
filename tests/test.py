import json

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client(tmp_path):
    seed_data = [
        {
            "id": 1,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+65 9123 4567",
        },
        {
            "id": 2,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+65 8234 5678",
        },
    ]
    data_file = tmp_path / "contacts.json"
    data_file.write_text(json.dumps(seed_data), encoding="utf-8")

    app = create_app(data_file=data_file)
    with TestClient(app) as test_client:
        yield test_client


def test_root_healthcheck(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_contact_by_id_success(client: TestClient):
    response = client.get("/contacts/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"


def test_get_contact_by_id_not_found(client: TestClient):
    response = client.get("/contacts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact 999 not found"


def test_add_contact_success_and_processed_by_service(client: TestClient):
    response = client.post(
        "/contacts",
        json={
            "name": "  New   Person ",
            "email": "NEW@MAIL.COM",
            "phone": "99238723",
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 3,
        "name": "New Person",
        "email": "new@mail.com",
        "phone": "+65 9923 8723",
    }


def test_add_contact_accepts_spaced_singapore_number(client: TestClient):
    response = client.post(
        "/contacts",
        json={
            "name": "Spaced Number",
            "email": "spaced@mail.com",
            "phone": "8234 7824",
        },
    )
    assert response.status_code == 201
    assert response.json()["phone"] == "+65 8234 7824"


def test_add_contact_validation_error(client: TestClient):
    response = client.post(
        "/contacts",
        json={
            "name": "",
            "email": "invalid-email",
            "phone": "abc",
        },
    )
    assert response.status_code == 422


def test_add_contact_rejects_non_singapore_mobile(client: TestClient):
    response = client.post(
        "/contacts",
        json={
            "name": "Invalid SG",
            "email": "valid@mail.com",
            "phone": "72345678",
        },
    )
    assert response.status_code == 422


def test_delete_contact_success(client: TestClient):
    response = client.delete("/contacts/2")
    assert response.status_code == 200
    assert response.json()["id"] == 2

    follow_up = client.get("/contacts/2")
    assert follow_up.status_code == 404


def test_delete_contact_path_validation(client: TestClient):
    response = client.delete("/contacts/0")
    assert response.status_code == 422
