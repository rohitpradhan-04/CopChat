import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

# Set test environment database before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from core.database import Base, getDbSession
from core.main import app
from core.security import create_access_token

# Create test engine using in-memory SQLite
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[getDbSession] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def test_user_registration_flow():
    payload = {
        "service_id": "COP-1001",
        "full_name": "Officer Arjun Verma",
        "rank": "Constable",
        "department": "law_and_order",
        "station": "North Zone PS",
        "role": "Patrol Officer",
        "date_of_joining": "2022-01-15",
        "mobile_number": "+919876543210",
        "email": "arjun.verma@copchat.com",
        "emergency_contact_name": "Ramesh Verma",
        "emergency_contact_number": "+919876543211",
        "blood_group": "O+",
    }

    response = client.post("/v1/register", json=payload)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["status"] == "success"
    assert "temp_password" in data
    assert len(data["temp_password"]) >= 8
    assert data["user"]["service_id"] == "COP-1001"
    assert data["user"]["is_first_login"] is True

    temp_password = data["temp_password"]

    # Test Login with temporary password
    login_payload = {
        "email_or_service_id": "COP-1001",
        "password": temp_password,
    }
    login_response = client.post("/v1/login", json=login_payload)
    assert login_response.status_code == 200, login_response.text

    login_data = login_response.json()
    assert login_data["is_first_login"] is True
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    # Test Login using Email instead of Service ID
    email_login_response = client.post(
        "/v1/login",
        json={
            "email_or_service_id": "arjun.verma@copchat.com",
            "password": temp_password,
        },
    )
    assert email_login_response.status_code == 200
    assert email_login_response.json()["is_first_login"] is True

    # Test Setup New Permanent Password
    setup_payload = {
        "email_or_service_id": "COP-1001",
        "current_password": temp_password,
        "new_password": "NewPermanentPass#2026",
    }
    setup_response = client.post("/v1/setup-password", json=setup_payload)
    assert setup_response.status_code == 200, setup_response.text

    setup_data = setup_response.json()
    assert setup_data["status"] == "success"
    assert setup_data["is_first_login"] is False

    # Test Login with old temporary password should fail
    old_login_response = client.post("/v1/login", json=login_payload)
    assert old_login_response.status_code == 401

    # Test Login with new permanent password should succeed with is_first_login=False
    new_login_response = client.post(
        "/v1/login",
        json={
            "email_or_service_id": "COP-1001",
            "password": "NewPermanentPass#2026",
        },
    )
    assert new_login_response.status_code == 200, new_login_response.text
    assert new_login_response.json()["is_first_login"] is False


def test_duplicate_user_registration():
    payload = {
        "service_id": "COP-2002",
        "full_name": "Officer Priya Sharma",
        "rank": "SI",
        "department": "cyber_crime",
        "date_of_joining": "2020-03-10",
        "mobile_number": "+919811122233",
        "email": "priya.sharma@copchat.com",
        "emergency_contact_name": "Amit Sharma",
        "emergency_contact_number": "+919811122234",
        "blood_group": "A+",
    }

    res1 = client.post("/v1/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/v1/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def _register_officer(
    service_id: str = "COP-3003",
    email: str = "neha.rao@copchat.com",
    mobile_number: str = "+919800011122",
):
    payload = {
        "service_id": service_id,
        "full_name": "Officer Neha Rao",
        "rank": "ASI",
        "department": "traffic",
        "station": "East Zone PS",
        "role": "Traffic Officer",
        "date_of_joining": "2021-07-20",
        "mobile_number": mobile_number,
        "email": email,
        "emergency_contact_name": "Suresh Rao",
        "emergency_contact_number": "+919800011123",
        "blood_group": "B+",
    }
    response = client.post("/v1/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_forgot_password_returns_generic_message_for_unknown_user():
    response = client.post(
        "/v1/forgot-password",
        json={"email_or_service_id": "unknown.user@copchat.com"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert "If an account exists" in data["message"]


def test_forgot_and_reset_password_flow():
    registration = _register_officer()
    temp_password = registration["temp_password"]
    user_id = registration["user"]["id"]

    # Complete first-login setup so the account has a permanent password
    setup_response = client.post(
        "/v1/setup-password",
        json={
            "email_or_service_id": "COP-3003",
            "current_password": temp_password,
            "new_password": "PermanentPass#2026",
        },
    )
    assert setup_response.status_code == 200, setup_response.text

    captured: dict[str, str] = {}

    def capture_reset_email(**kwargs):
        captured["reset_token"] = kwargs["reset_token"]
        captured["to_email"] = kwargs["to_email"]
        return True

    with patch(
        "core.routers.v1.user.send_password_reset_email",
        side_effect=capture_reset_email,
    ):
        forgot_response = client.post(
            "/v1/forgot-password",
            json={"email_or_service_id": "neha.rao@copchat.com"},
        )

    assert forgot_response.status_code == 200, forgot_response.text
    assert "If an account exists" in forgot_response.json()["message"]
    assert "reset_token" in captured
    assert captured["to_email"] == "neha.rao@copchat.com"

    # Invalid token should fail
    invalid_reset = client.post(
        "/v1/reset-password",
        json={
            "reset_token": "not-a-valid-token",
            "new_password": "ShouldNotWork#1",
        },
    )
    assert invalid_reset.status_code == 400
    assert "Invalid or expired" in invalid_reset.json()["detail"]

    # Access token must not be accepted as a reset token
    access_token = create_access_token(
        data={
            "sub": str(user_id),
            "email": "neha.rao@copchat.com",
            "is_first_login": False,
        }
    )
    wrong_type_reset = client.post(
        "/v1/reset-password",
        json={
            "reset_token": access_token,
            "new_password": "ShouldNotWork#2",
        },
    )
    assert wrong_type_reset.status_code == 400

    # Valid reset token updates password
    reset_response = client.post(
        "/v1/reset-password",
        json={
            "reset_token": captured["reset_token"],
            "new_password": "ResetPass#2026",
        },
    )
    assert reset_response.status_code == 200, reset_response.text
    reset_data = reset_response.json()
    assert reset_data["status"] == "success"
    assert reset_data["is_first_login"] is False

    # Old permanent password should no longer work
    old_login = client.post(
        "/v1/login",
        json={
            "email_or_service_id": "COP-3003",
            "password": "PermanentPass#2026",
        },
    )
    assert old_login.status_code == 401

    # New password should work
    new_login = client.post(
        "/v1/login",
        json={
            "email_or_service_id": "COP-3003",
            "password": "ResetPass#2026",
        },
    )
    assert new_login.status_code == 200, new_login.text
    assert new_login.json()["is_first_login"] is False


def test_forgot_password_by_service_id_sends_email():
    _register_officer(
        service_id="COP-4004",
        email="kiran.das@copchat.com",
        mobile_number="+919822233344",
    )

    captured: dict[str, str] = {}

    def capture_reset_email(**kwargs):
        captured["service_id"] = kwargs["service_id"]
        captured["reset_token"] = kwargs["reset_token"]
        return True

    with patch(
        "core.routers.v1.user.send_password_reset_email",
        side_effect=capture_reset_email,
    ):
        response = client.post(
            "/v1/forgot-password",
            json={"email_or_service_id": "COP-4004"},
        )

    assert response.status_code == 200
    assert captured["service_id"] == "COP-4004"
    assert captured["reset_token"]
