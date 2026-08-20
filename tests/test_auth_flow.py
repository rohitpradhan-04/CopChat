import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

# Set test environment database before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from core.database import Base, getDbSession
from core.main import app

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
