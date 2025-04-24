from sqlalchemy import Column, String, Boolean, Text
from src.database.db import Base

class SwiftCode(Base):
    __tablename__ = "swift_codes"

    swift_code = Column(String(11), primary_key=True, index=True)
    bank_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    country_iso2 = Column(String(2), nullable=False, index=True)
    country_name = Column(String(255), nullable=False)
    is_headquarter = Column(Boolean, default=False)