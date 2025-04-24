from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any, cast

from src.database.models import SwiftCode


class SwiftCodeRepository:

    @staticmethod
    def get_swift_code(db: Session, swift_code: str) -> Optional[SwiftCode]:
        return db.query(SwiftCode).filter(SwiftCode.swift_code == swift_code).first()

    @staticmethod
    def get_branches_for_headquarters(db: Session, headquarters_code: str) -> List[SwiftCode]:
        hq_prefix = headquarters_code[:8]

        result = db.query(SwiftCode).filter(
            and_(
                func.substr(SwiftCode.swift_code, 1, 8) == hq_prefix,
                SwiftCode.swift_code != headquarters_code,
                SwiftCode.is_headquarter == False
            )
        ).all()

        return cast(List[SwiftCode], result)

    @staticmethod
    def get_country_swift_codes(db: Session, country_iso2: str) -> List[SwiftCode]:
        country_iso2 = country_iso2.upper()

        result = db.query(SwiftCode).filter(SwiftCode.country_iso2 == country_iso2).all()
        return cast(List[SwiftCode], result)

    @staticmethod
    def create_swift_code(db: Session, swift_data: Dict[str, Any]) -> SwiftCode:

        new_code = SwiftCode(**swift_data)
        db.add(new_code)
        db.commit()
        db.refresh(new_code)
        return new_code

    @staticmethod
    def delete_swift_code(db: Session, swift_code: str) -> bool:

        code = db.query(SwiftCode).filter(SwiftCode.swift_code == swift_code).first()

        if not code:
            return False

        db.delete(code)
        db.commit()
        return True

    @staticmethod
    def bulk_create_swift_codes(db: Session, swift_codes_data: List[Dict[str, Any]]) -> None:

        for swift_data in swift_codes_data:
            existing = db.query(SwiftCode).filter(
                SwiftCode.swift_code == swift_data["swift_code"]
            ).first()

            if not existing:
                new_code = SwiftCode(**swift_data)
                db.add(new_code)

        db.commit()