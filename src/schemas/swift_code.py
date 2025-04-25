from pydantic import BaseModel, Field, field_validator
from typing import List


class SwiftCodeBase(BaseModel):
    address: str
    bankName: str
    countryISO2: str
    isHeadquarter: bool
    swiftCode: str

    @field_validator("countryISO2", mode="before")
    def uppercase_country_iso(cls, value: str) -> str:
        return value.upper()


class SwiftCodeCreate(SwiftCodeBase):
    countryName: str

    @field_validator("countryName", mode="before")
    def uppercase_country_name(cls, value: str) -> str:
        return value.upper()


class SwiftCodeResponse(SwiftCodeBase):
    countryName: str

    model_config = {
        "from_attributes": True
    }


class SwiftCodeWithBranches(SwiftCodeResponse):
    branches: List[SwiftCodeBase] = Field(default_factory=list)


class CountrySwiftCodes(BaseModel):
    countryISO2: str
    countryName: str
    swiftCodes: List[SwiftCodeBase]


class MessageResponse(BaseModel):
    message: str
