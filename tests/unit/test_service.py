import pytest
import tempfile
import pandas as pd
import os
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from src.services.swift_service import SwiftCodeService
from src.repositories.swift_repository import SwiftCodeRepository
from src.database.models import SwiftCode


@pytest.fixture
def mock_swift_code():
    code = MagicMock(spec=SwiftCode)
    code.swift_code = "ABCDUS33XXX"
    code.bank_name = "Test Bank HQ"
    code.address = "123 Main St, New York"
    code.country_iso2 = "US"
    code.country_name = "UNITED STATES"
    code.is_headquarter = True
    return code


@pytest.fixture
def mock_branch_code():
    code = MagicMock(spec=SwiftCode)
    code.swift_code = "ABCDUS66"
    code.bank_name = "Test Bank Branch"
    code.address = "456 Side St, Chicago"
    code.country_iso2 = "US"
    code.country_name = "UNITED STATES"
    code.is_headquarter = False
    return code


def test_get_swift_code_hq(mock_swift_code, mock_branch_code):
    mock_db = MagicMock()

    with patch.object(
            SwiftCodeRepository, 'get_swift_code', return_value=mock_swift_code
    ) as mock_get_code:
        with patch.object(
                SwiftCodeRepository, 'get_branches_for_headquarters', return_value=[mock_branch_code]
        ) as mock_get_branches:
            result = SwiftCodeService.get_swift_code(mock_db, "ABCDUS33XXX")

            mock_get_code.assert_called_once_with(mock_db, "ABCDUS33XXX")
            mock_get_branches.assert_called_once_with(mock_db, "ABCDUS33XXX")

            assert result is not None
            assert result["swiftCode"] == "ABCDUS33XXX"
            assert result["bankName"] == "Test Bank HQ"
            assert result["isHeadquarter"] == True
            assert len(result["branches"]) == 1
            assert result["branches"][0]["swiftCode"] == "ABCDUS66"
            assert result["branches"][0]["bankName"] == "Test Bank Branch"


def test_get_swift_code_branch(mock_branch_code):
    mock_db = MagicMock()

    with patch.object(
            SwiftCodeRepository, 'get_swift_code', return_value=mock_branch_code
    ) as mock_get_code:
        result = SwiftCodeService.get_swift_code(mock_db, "ABCDUS66")

        mock_get_code.assert_called_once_with(mock_db, "ABCDUS66")

        assert result is not None
        assert result["swiftCode"] == "ABCDUS66"
        assert result["bankName"] == "Test Bank Branch"
        assert result["isHeadquarter"] == False
        assert "branches" not in result


def test_get_swift_code_not_found():
    mock_db = MagicMock()

    with patch.object(
            SwiftCodeRepository, 'get_swift_code', return_value=None
    ) as mock_get_code:
        result = SwiftCodeService.get_swift_code(mock_db, "NONEXISTENT")

        mock_get_code.assert_called_once_with(mock_db, "NONEXISTENT")

        assert result is None


def test_get_country_swift_codes(mock_swift_code, mock_branch_code):
    mock_db = MagicMock()

    with patch.object(
            SwiftCodeRepository, 'get_country_swift_codes', return_value=[mock_swift_code, mock_branch_code]
    ) as mock_get_codes:
        result = SwiftCodeService.get_country_swift_codes(mock_db, "US")

        mock_get_codes.assert_called_once_with(mock_db, "US")

        assert result is not None
        assert result["countryISO2"] == "US"
        assert result["countryName"] == "UNITED STATES"
        assert len(result["swiftCodes"]) == 2
        assert result["swiftCodes"][0]["swiftCode"] == "ABCDUS33XXX"
        assert result["swiftCodes"][1]["swiftCode"] == "ABCDUS66"


def test_get_country_swift_codes_not_found():
    mock_db = MagicMock()

    with patch.object(
            SwiftCodeRepository, 'get_country_swift_codes', return_value=[]
    ) as mock_get_codes:
        result = SwiftCodeService.get_country_swift_codes(mock_db, "XX")

        mock_get_codes.assert_called_once_with(mock_db, "XX")

        assert result is None


def test_create_swift_code():
    mock_db = MagicMock()

    swift_data = {
        "swiftCode": "NEWWUS22",
        "bankName": "New Bank",
        "address": "789 New St, Boston",
        "countryISO2": "us",
        "countryName": "United States",
        "isHeadquarter": False
    }

    expected_data = {
        "swift_code": "NEWWUS22",
        "bank_name": "New Bank",
        "address": "789 New St, Boston",
        "country_iso2": "US",
        "country_name": "UNITED STATES",
        "is_headquarter": False
    }

    with patch.object(
            SwiftCodeRepository, 'get_swift_code', return_value=None
    ) as mock_get_code:
        with patch.object(
                SwiftCodeRepository, 'create_swift_code', return_value=MagicMock()
        ) as mock_create_code:
            result = SwiftCodeService.create_swift_code(mock_db, swift_data)

            mock_get_code.assert_called_once_with(mock_db, "NEWWUS22")
            mock_create_code.assert_called_once()
            args, _ = mock_create_code.call_args
            assert args[1] == expected_data

            assert "message" in result
            assert "NEWWUS22" in result["message"]


def test_create_duplicate_swift_code():
    mock_db = MagicMock()
    mock_existing_code = MagicMock(spec=SwiftCode)

    swift_data = {
        "swiftCode": "EXISTING",
        "bankName": "Duplicate Bank",
        "address": "123 Duplicate St",
        "countryISO2": "US",
        "countryName": "United States",
        "isHeadquarter": True
    }

    with patch.object(
            SwiftCodeRepository, 'get_swift_code', return_value=mock_existing_code
    ) as mock_get_code:
        with pytest.raises(HTTPException) as exc_info:
            SwiftCodeService.create_swift_code(mock_db, swift_data)

        mock_get_code.assert_called_once_with(mock_db, "EXISTING")

        assert exc_info.value.status_code == 409


def test_delete_swift_code():
    mock_db = MagicMock()

    with patch.object(
            SwiftCodeRepository, 'delete_swift_code', return_value=True
    ) as mock_delete_code:
        result = SwiftCodeService.delete_swift_code(mock_db, "ABCDUS66")

        mock_delete_code.assert_called_once_with(mock_db, "ABCDUS66")

        assert "message" in result
        assert "ABCDUS66" in result["message"]


def test_delete_swift_code_not_found():
    mock_db = MagicMock()

    with patch.object(
            SwiftCodeRepository, 'delete_swift_code', return_value=False
    ) as mock_delete_code:
        with pytest.raises(HTTPException) as exc_info:
            SwiftCodeService.delete_swift_code(mock_db, "NONEXISTENT")

        mock_delete_code.assert_called_once_with(mock_db, "NONEXISTENT")

        assert exc_info.value.status_code == 404


def test_seed_database():
    mock_db = MagicMock()

    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        test_data = pd.DataFrame({
            'country_iso2_code': ['US', 'us'],
            'swift_code': ['ABCDUS33XXX', 'ABCDUS66'],
            'name': ['Test Bank HQ', 'Test Bank Branch'],
            'address': ['123 Main St, New York', '456 Side St, Chicago'],
            'country_name': ['United States', 'united states']
        })
        test_data.to_csv(temp_file.name, index=False)

    try:
        expected_data = [
            {
                "swiftCode": "ABCDUS33XXX",
                "bankName": "Test Bank HQ",
                "address": "123 Main St, New York",
                "countryISO2": "US",
                "countryName": "UNITED STATES",
                "isHeadquarter": True
            },
            {
                "swiftCode": "ABCDUS66",
                "bankName": "Test Bank Branch",
                "address": "456 Side St, Chicago",
                "countryISO2": "US",
                "countryName": "UNITED STATES",
                "isHeadquarter": False
            }
        ]

        with patch.object(
                SwiftCodeRepository, 'bulk_create_swift_codes'
        ) as mock_bulk_create:
            SwiftCodeService.seed_database(mock_db, temp_file.name)

            mock_bulk_create.assert_called_once()

            args, _ = mock_bulk_create.call_args
            assert len(args) == 2
            assert args[0] == mock_db

            assert isinstance(args[1], list)
            assert all(isinstance(item, dict) for item in args[1])
            assert args[1] == expected_data

    finally:
        os.unlink(temp_file.name)