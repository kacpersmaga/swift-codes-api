import pytest
from src.utils.parser import SwiftCodeParser


class TestSwiftCodeParser:

    def test_parse_csv(self, tmp_path):
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
        assert code1["swiftCode"] == "BOAUSXXXXX"
        assert code1["bankName"] == "BANK OF AMERICA"
        assert code1["countryISO2"] == "US"
        assert code1["countryName"] == "UNITED STATES"
        assert code1["isHeadquarter"] is True

        code2 = swift_codes[1]
        assert code2["swiftCode"] == "BOAUS1234"
        assert code2["isHeadquarter"] is False

    def test_associate_branches_with_headquarters(self):
        swift_codes = [
            {
                "swiftCode": "BOAUSXXXXX",
                "bankName": "BANK OF AMERICA",
                "address": "100 Main St, New York",
                "countryISO2": "US",
                "countryName": "UNITED STATES",
                "isHeadquarter": True
            },
            {
                "swiftCode": "BOAUSXXX1",
                "bankName": "BANK OF AMERICA BRANCH",
                "address": "200 Main St, Chicago",
                "countryISO2": "US",
                "countryName": "UNITED STATES",
                "isHeadquarter": False
            },
            {
                "swiftCode": "HSBBGBXXXX",
                "bankName": "HSBC BANK UK",
                "address": "1 Canada Square",
                "countryISO2": "UK",
                "countryName": "UNITED KINGDOM",
                "isHeadquarter": True
            },
            {
                "swiftCode": "HSBBGBXX45",
                "bankName": "HSBC BRANCH UK",
                "address": "10 High Street",
                "countryISO2": "UK",
                "countryName": "UNITED KINGDOM",
                "isHeadquarter": False
            }
        ]

        hq_to_branches = SwiftCodeParser.associate_branches_with_headquarters(swift_codes)

        assert "BOAUSXXXXX" in hq_to_branches
        assert "HSBBGBXXXX" in hq_to_branches

        assert "BOAUSXXX1" in hq_to_branches["BOAUSXXXXX"]
        assert "HSBBGBXX45" in hq_to_branches["HSBBGBXXXX"]

    def test_parse_csv_missing_columns(self, tmp_path):
        csv_data = "SWIFT CODE,NAME,ADDRESS\nBOAUSXXXXX,BANK OF AMERICA,100 Main St"
        csv_file = tmp_path / "missing_cols.csv"
        csv_file.write_text(csv_data)

        with pytest.raises(ValueError, match="Missing required columns"):
            SwiftCodeParser.parse_csv(str(csv_file))

    def test_branch_with_no_matching_headquarter(self):
        swift_codes = [
            {
                "swiftCode": "XYZABC1234",
                "bankName": "Lone Branch",
                "address": "Unknown",
                "countryISO2": "ZZ",
                "countryName": "NOWHERE",
                "isHeadquarter": False
            }
        ]

        result = SwiftCodeParser.associate_branches_with_headquarters(swift_codes)
        assert result == {}

    def test_parse_csv_with_extra_columns(self, tmp_path):
        csv_data = """COUNTRY ISO2 CODE,SWIFT CODE,CODE TYPE,NAME,ADDRESS,TOWN NAME,COUNTRY NAME,TIME ZONE,EXTRA COL
US,BOAUSXXXXX,XXX,BANK OF AMERICA,"100 Main St",New York,UNITED STATES,EST,SHOULD_BE_IGNORED
"""
        csv_file = tmp_path / "extra_cols.csv"
        csv_file.write_text(csv_data)

        swift_codes = SwiftCodeParser.parse_csv(str(csv_file))

        assert len(swift_codes) == 1
        assert swift_codes[0]["swiftCode"] == "BOAUSXXXXX"
        assert swift_codes[0]["bankName"] == "BANK OF AMERICA"
