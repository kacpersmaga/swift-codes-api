import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class SwiftCodeParser:

    @staticmethod
    def parse_csv(file_path: str) -> List[Dict[str, Any]]:

        try:
            logger.info(f"Parsing CSV file: {file_path}")

            df = pd.read_csv(file_path)

            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

            required_columns = ['country_iso2_code', 'swift_code', 'name', 'address', 'country_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns in CSV: {missing_columns}")

            swift_codes = []
            for _, row in df.iterrows():
                country_iso2 = row['country_iso2_code'].strip().upper()
                country_name = row['country_name'].strip().upper()
                swift_code = row['swift_code'].strip()
                bank_name = row['name'].strip()
                address = row['address'].strip()

                is_headquarter = swift_code.endswith('XXX')

                swift_code_data = {
                    "swift_code": swift_code,
                    "bank_name": bank_name,
                    "address": address,
                    "country_iso2": country_iso2,
                    "country_name": country_name,
                    "is_headquarter": is_headquarter,
                }

                swift_codes.append(swift_code_data)

            logger.info(f"Successfully parsed {len(swift_codes)} SWIFT codes")
            return swift_codes

        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise

    @staticmethod
    def associate_branches_with_headquarters(swift_codes: List[Dict[str, Any]]) -> Dict[str, List[str]]:

        hq_to_branches = {}

        first_8_to_hq = {}

        for swift_code_data in swift_codes:
            swift_code = swift_code_data["swiftCode"]
            is_headquarter = swift_code_data["isHeadquarter"]

            if is_headquarter:
                first_8 = swift_code[:8]
                first_8_to_hq[first_8] = swift_code
                hq_to_branches[swift_code] = []

        for swift_code_data in swift_codes:
            swift_code = swift_code_data["swiftCode"]
            is_headquarter = swift_code_data["isHeadquarter"]

            if not is_headquarter:
                first_8 = swift_code[:8]
                if first_8 in first_8_to_hq:
                    hq_code = first_8_to_hq[first_8]
                    hq_to_branches[hq_code].append(swift_code)

        return hq_to_branches