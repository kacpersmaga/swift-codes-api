import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.db import Base
from src.database.models import SwiftCode
from src.repositories.swift_repository import SwiftCodeRepository

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    hq_code = SwiftCode(
        swift_code="ABCDUS33XXX",
        bank_name="Test Bank HQ",
        address="123 Main St, New York",
        country_iso2="US",
        country_name="UNITED STATES",
        is_headquarter=True
    )

    branch_code = SwiftCode(
        swift_code="ABCDUS33BRN",
        bank_name="Test Bank Branch",
        address="456 Side St, Chicago",
        country_iso2="US",
        country_name="UNITED STATES",
        is_headquarter=False
    )

    another_hq_code = SwiftCode(
        swift_code="EFGHUS33XXX",
        bank_name="Another Bank HQ",
        address="789 Wall St, New York",
        country_iso2="US",
        country_name="UNITED STATES",
        is_headquarter=True
    )

    another_branch_code = SwiftCode(
        swift_code="EFGHUS33BRN",
        bank_name="Another Bank Branch",
        address="321 Branch St, Boston",
        country_iso2="US",
        country_name="UNITED STATES",
        is_headquarter=False
    )

    foreign_code = SwiftCode(
        swift_code="IJKLCA33XXX",
        bank_name="Foreign Bank",
        address="999 Foreign St, Toronto",
        country_iso2="CA",
        country_name="CANADA",
        is_headquarter=True
    )

    db.add_all([hq_code, branch_code, another_hq_code, another_branch_code, foreign_code])
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


def test_get_swift_code(test_db):
    code = SwiftCodeRepository.get_swift_code(test_db, "ABCDUS33XXX")
    assert code is not None
    assert code.swift_code == "ABCDUS33XXX"
    assert code.bank_name == "Test Bank HQ"
    assert code.is_headquarter is True

    code = SwiftCodeRepository.get_swift_code(test_db, "NONEXISTENT")
    assert code is None


def test_get_branches_for_headquarters(test_db):
    branches = SwiftCodeRepository.get_branches_for_headquarters(test_db, "ABCDUS33XXX")
    assert len(branches) == 1
    assert branches[0].swift_code == "ABCDUS33BRN"
    assert branches[0].is_headquarter is False

    branches = SwiftCodeRepository.get_branches_for_headquarters(test_db, "EFGHUS33XXX")
    assert len(branches) == 1
    assert branches[0].swift_code == "EFGHUS33BRN"

    branches = SwiftCodeRepository.get_branches_for_headquarters(test_db, "NONEXISTENT")
    assert len(branches) == 0

    branches = SwiftCodeRepository.get_branches_for_headquarters(test_db, "ABCDUS33BRN")
    assert len(branches) == 0


def test_get_country_swift_codes(test_db):
    codes = SwiftCodeRepository.get_country_swift_codes(test_db, "US")
    assert len(codes) == 4

    codes = SwiftCodeRepository.get_country_swift_codes(test_db, "CA")
    assert len(codes) == 1
    assert codes[0].swift_code == "IJKLCA33XXX"

    codes = SwiftCodeRepository.get_country_swift_codes(test_db, "XX")
    assert len(codes) == 0

    codes = SwiftCodeRepository.get_country_swift_codes(test_db, "ca")
    assert len(codes) == 1


def test_create_swift_code(test_db):
    new_code_data = {
        "swift_code": "NEWWUS22",
        "bank_name": "New Bank",
        "address": "789 New St, Boston",
        "country_iso2": "US",
        "country_name": "UNITED STATES",
        "is_headquarter": False
    }

    new_code = SwiftCodeRepository.create_swift_code(test_db, new_code_data)
    assert new_code.swift_code == "NEWWUS22"
    assert new_code.bank_name == "New Bank"

    code = SwiftCodeRepository.get_swift_code(test_db, "NEWWUS22")
    assert code is not None
    assert code.bank_name == "New Bank"


def test_delete_swift_code(test_db):
    result = SwiftCodeRepository.delete_swift_code(test_db, "ABCDUS33BRN")
    assert result is True

    code = SwiftCodeRepository.get_swift_code(test_db, "ABCDUS33BRN")
    assert code is None

    result = SwiftCodeRepository.delete_swift_code(test_db, "NONEXISTENT")
    assert result is False


def test_bulk_create_swift_codes(test_db):
    bulk_codes = [
        {
            "swift_code": "BULK1US22",
            "bank_name": "Bulk Bank 1",
            "address": "1 Bulk St, New York",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": True
        },
        {
            "swift_code": "BULK2US33",
            "bank_name": "Bulk Bank 2",
            "address": "2 Bulk St, Chicago",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": False
        },
        {
            "swift_code": "ABCDUS33XXX",
            "bank_name": "This Should Be Skipped",
            "address": "Skip St, Nowhere",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": True
        }
    ]

    SwiftCodeRepository.bulk_create_swift_codes(test_db, bulk_codes)

    code1 = SwiftCodeRepository.get_swift_code(test_db, "BULK1US22")
    assert code1 is not None
    assert code1.bank_name == "Bulk Bank 1"

    code2 = SwiftCodeRepository.get_swift_code(test_db, "BULK2US33")
    assert code2 is not None
    assert code2.bank_name == "Bulk Bank 2"

    existing = SwiftCodeRepository.get_swift_code(test_db, "ABCDUS33XXX")
    assert existing is not None
    assert existing.bank_name == "Test Bank HQ"
