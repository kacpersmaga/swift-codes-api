import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database.db import Base, get_db
from src.database.models import SwiftCode

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    hq_code = SwiftCode(
        swift_code="BANKUS33XXX",
        bank_name="Bank USA HQ",
        address="1 Main St, New York",
        country_iso2="US",
        country_name="UNITED STATES",
        is_headquarter=True
    )

    branch_code = SwiftCode(
        swift_code="BANKUS33BRN",
        bank_name="Bank USA Branch",
        address="2 Branch St, Chicago",
        country_iso2="US",
        country_name="UNITED STATES",
        is_headquarter=False
    )

    foreign_hq = SwiftCode(
        swift_code="FOREIGNCA1XXX",
        bank_name="Foreign Bank HQ",
        address="3 Maple St, Toronto",
        country_iso2="CA",
        country_name="CANADA",
        is_headquarter=True
    )

    db.add_all([hq_code, branch_code, foreign_hq])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "SWIFT Codes API is running"}


def test_get_hq_swift_code():
    response = client.get("/v1/swift-codes/BANKUS33XXX")
    assert response.status_code == 200
    data = response.json()

    assert data["swiftCode"] == "BANKUS33XXX"
    assert data["bankName"] == "Bank USA HQ"
    assert data["isHeadquarter"] is True
    assert len(data["branches"]) == 1
    assert data["branches"][0]["swiftCode"] == "BANKUS33BRN"


def test_get_branch_swift_code():
    response = client.get("/v1/swift-codes/BANKUS33BRN")
    assert response.status_code == 200
    data = response.json()

    assert data["swiftCode"] == "BANKUS33BRN"
    assert data["bankName"] == "Bank USA Branch"
    assert data["isHeadquarter"] is False
    assert isinstance(data["branches"], list)
    assert len(data["branches"]) == 0


def test_get_nonexistent_swift_code():
    response = client.get("/v1/swift-codes/NONEXISTENT")
    assert response.status_code == 404


def test_get_country_swift_codes():
    response = client.get("/v1/swift-codes/country/US")
    assert response.status_code == 200
    data = response.json()

    assert data["countryISO2"] == "US"
    assert data["countryName"] == "UNITED STATES"
    assert len(data["swiftCodes"]) == 2

    swift_codes = {code["swiftCode"] for code in data["swiftCodes"]}
    assert "BANKUS33XXX" in swift_codes
    assert "BANKUS33BRN" in swift_codes


def test_get_country_swift_codes_case_insensitive():
    response = client.get("/v1/swift-codes/country/us")
    assert response.status_code == 200
    data = response.json()
    assert data["countryISO2"] == "US"


def test_get_country_swift_codes_not_found():
    response = client.get("/v1/swift-codes/country/ZZ")
    assert response.status_code == 404


def test_create_swift_code():
    new_code = {
        "swiftCode": "NEWBANKUS22",
        "bankName": "New Bank USA",
        "address": "4 New St, Miami",
        "countryISO2": "us",
        "countryName": "united states",
        "isHeadquarter": False
    }

    response = client.post("/v1/swift-codes", json=new_code)
    assert response.status_code == 201
    assert "message" in response.json()

    get_response = client.get("/v1/swift-codes/NEWBANKUS22")
    assert get_response.status_code == 200
    assert get_response.json()["swiftCode"] == "NEWBANKUS22"


def test_create_duplicate_swift_code():
    duplicate = {
        "swiftCode": "BANKUS33XXX",
        "bankName": "Duplicate Bank",
        "address": "5 Duplicate St",
        "countryISO2": "US",
        "countryName": "United States",
        "isHeadquarter": True
    }

    response = client.post("/v1/swift-codes", json=duplicate)
    assert response.status_code == 409


def test_delete_swift_code():
    response = client.delete("/v1/swift-codes/BANKUS33BRN")
    assert response.status_code == 200
    assert "message" in response.json()

    get_response = client.get("/v1/swift-codes/BANKUS33BRN")
    assert get_response.status_code == 404


def test_delete_nonexistent_swift_code():
    response = client.delete("/v1/swift-codes/NONEXISTENT")
    assert response.status_code == 404
