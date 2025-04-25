import pytest
from src.utils.parser import SwiftCodeParser

def test_parse_csv(tmp_path):
    csv_data = """COUNTRY ISO2 CODE,SWIFT CODE,CODE TYPE,NAME,ADDRESS,TOWN NAME,COUNTRY NAME,TIME ZONE
US,BOAUSXXXXX,XXX,BANK OF AMERICA,"100 Main St, New York",New York,UNITED STATES,EST
US,BOAUS1234,XXX,BANK OF AMERICA BRANCH,"200 Main St, Chicago",Chicago,UNITED STATES,CST
UK,HSBBGBXXXX,XXX,HSBC BANK UK,"1 Canada Square",London,UNITED KINGDOM,GMT
UK,HSBBGB2345,XXX,HSBC BRANCH UK,"10 High Street",Manchester,UNITED KINGDOM,GMT
"""
    csv_file = tmp_path / "test_swift_codes.csv"
    csv_file.write_text(csv_data)

    swift_codes = SwiftCodeParser.parse_csv(str(csv_file))

    assert len(swift_codes) == 4

    code1 = swift_codes[0]
    assert code1["swift_code"] == "BOAUSXXXXX"
    assert code1["bank_name"] == "BANK OF AMERICA"
    assert code1["address"] == "100 Main St, New York"
    assert code1["country_iso2"] == "US"
    assert code1["country_name"] == "UNITED STATES"
    assert code1["is_headquarter"] is True

    code2 = swift_codes[1]
    assert code2["swift_code"] == "BOAUS1234"
    assert code2["bank_name"] == "BANK OF AMERICA BRANCH"
    assert code2["is_headquarter"] is False


def test_associate_branches_with_headquarters():
    swift_codes = [
        {
            "swift_code": "BOAUSXXXXX",
            "bank_name": "BANK OF AMERICA",
            "address": "100 Main St, New York",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": True
        },
        {
            "swift_code": "BOAUSXXX1",
            "bank_name": "BANK OF AMERICA BRANCH",
            "address": "200 Main St, Chicago",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": False
        },
        {
            "swift_code": "HSBBGBXXXX",
            "bank_name": "HSBC BANK UK",
            "address": "1 Canada Square",
            "country_iso2": "UK",
            "country_name": "UNITED KINGDOM",
            "is_headquarter": True
        },
        {
            "swift_code": "HSBBGBXX45",
            "bank_name": "HSBC BRANCH UK",
            "address": "10 High Street",
            "country_iso2": "UK",
            "country_name": "UNITED KINGDOM",
            "is_headquarter": False
        }
    ]

    hq_to_branches = SwiftCodeParser.associate_branches_with_headquarters(swift_codes)

    assert "BOAUSXXXXX" in hq_to_branches
    assert "HSBBGBXXXX" in hq_to_branches
    assert "BOAUSXXX1" in hq_to_branches["BOAUSXXXXX"]
    assert "HSBBGBXX45" in hq_to_branches["HSBBGBXXXX"]


def test_parse_csv_missing_columns(tmp_path):
    csv_data = "SWIFT CODE,NAME,ADDRESS\nBOAUSXXXXX,BANK OF AMERICA,100 Main St"
    csv_file = tmp_path / "missing_cols.csv"
    csv_file.write_text(csv_data)

    with pytest.raises(ValueError, match="Missing required columns"):
        SwiftCodeParser.parse_csv(str(csv_file))


def test_branch_with_no_matching_headquarter():
    swift_codes = [
        {
            "swift_code": "XYZABC1234",
            "bank_name": "Lone Branch",
            "address": "Unknown",
            "country_iso2": "ZZ",
            "country_name": "NOWHERE",
            "is_headquarter": False
        }
    ]

    result = SwiftCodeParser.associate_branches_with_headquarters(swift_codes)
    assert result == {}


def test_parse_csv_with_extra_columns(tmp_path):
    csv_data = """COUNTRY ISO2 CODE,SWIFT CODE,CODE TYPE,NAME,ADDRESS,TOWN NAME,COUNTRY NAME,TIME ZONE,EXTRA COL
US,BOAUSXXXXX,XXX,BANK OF AMERICA,"100 Main St",New York,UNITED STATES,EST,SHOULD_BE_IGNORED
"""
    csv_file = tmp_path / "extra_cols.csv"
    csv_file.write_text(csv_data)

    swift_codes = SwiftCodeParser.parse_csv(str(csv_file))

    assert len(swift_codes) == 1
    code = swift_codes[0]
    assert code["swift_code"] == "BOAUSXXXXX"
    assert code["bank_name"] == "BANK OF AMERICA"
    assert code["address"] == "100 Main St"
    assert code["country_iso2"] == "US"
    assert code["country_name"] == "UNITED STATES"
    assert code["is_headquarter"] is True
