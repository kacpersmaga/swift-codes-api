from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from src.repositories.swift_repository import SwiftCodeRepository
from src.utils.parser import SwiftCodeParser


class SwiftCodeService:

    @staticmethod
    def seed_database(db: Session, file_path: str) -> None:

        swift_codes = SwiftCodeParser.parse_csv(file_path)

        SwiftCodeRepository.bulk_create_swift_codes(db, swift_codes)

    @staticmethod
    def get_swift_code(db: Session, swift_code: str) -> Optional[Dict[str, Any]]:

        code = SwiftCodeRepository.get_swift_code(db, swift_code)

        if not code:
            return None

        result = {
            "address": code.address,
            "bankName": code.bank_name,
            "countryISO2": code.country_iso2,
            "countryName": code.country_name,
            "isHeadquarter": code.is_headquarter,
            "swiftCode": code.swift_code
        }

        if code.is_headquarter:
            branches = SwiftCodeRepository.get_branches_for_headquarters(db, swift_code)

            result["branches"] = [
                {
                    "address": branch.address,
                    "bankName": branch.bank_name,
                    "countryISO2": branch.country_iso2,
                    "isHeadquarter": branch.is_headquarter,
                    "swiftCode": branch.swift_code
                }
                for branch in branches
            ]

        return result

    @staticmethod
    def get_country_swift_codes(db: Session, country_iso2: str) -> Optional[Dict[str, Any]]:

        codes = SwiftCodeRepository.get_country_swift_codes(db, country_iso2)

        if not codes or len(codes) == 0:
            return None

        country_name = codes[0].country_name

        return {
            "countryISO2": country_iso2.upper(),
            "countryName": country_name,
            "swiftCodes": [
                {
                    "address": code.address,
                    "bankName": code.bank_name,
                    "countryISO2": code.country_iso2,
                    "isHeadquarter": code.is_headquarter,
                    "swiftCode": code.swift_code
                }
                for code in codes
            ]
        }

    @staticmethod
    def create_swift_code(db: Session, swift_data: Dict[str, Any]) -> Dict[str, str]:

        db_swift_data = {
            "swift_code": swift_data["swiftCode"],
            "bank_name": swift_data["bankName"],
            "address": swift_data["address"],
            "country_iso2": swift_data["countryISO2"].upper(),
            "country_name": swift_data["countryName"].upper(),
            "is_headquarter": swift_data["isHeadquarter"]
        }

        existing = SwiftCodeRepository.get_swift_code(db, db_swift_data["swift_code"])

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"SWIFT code {db_swift_data['swift_code']} already exists"
            )

        SwiftCodeRepository.create_swift_code(db, db_swift_data)

        return {"message": f"SWIFT code {db_swift_data['swift_code']} added successfully"}

    @staticmethod
    def delete_swift_code(db: Session, swift_code: str) -> Dict[str, str]:

        deleted = SwiftCodeRepository.delete_swift_code(db, swift_code)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SWIFT code {swift_code} not found"
            )

        return {"message": f"SWIFT code {swift_code} deleted successfully"}