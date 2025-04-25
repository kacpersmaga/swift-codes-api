from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.swift_code import SwiftCodeCreate, SwiftCodeWithBranches, CountrySwiftCodes, \
    MessageResponse
from src.services.swift_service import SwiftCodeService

router = APIRouter(prefix="/v1/swift-codes", tags=["swift-codes"])


@router.get("/{swift_code}", response_model=SwiftCodeWithBranches)
def get_swift_code(swift_code: str, db: Session = Depends(get_db)):
    """
    Retrieve details of a single SWIFT code.
    If the code is for a headquarters, it will include details of all branch codes.
    """
    result = SwiftCodeService.get_swift_code(db, swift_code)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SWIFT code {swift_code} not found"
        )

    return result


@router.get("/country/{country_iso2}", response_model=CountrySwiftCodes)
def get_country_swift_codes(country_iso2: str, db: Session = Depends(get_db)):
    """
    Return all SWIFT codes with details for a specific country.
    """
    result = SwiftCodeService.get_country_swift_codes(db, country_iso2)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No SWIFT codes found for country {country_iso2}"
        )

    return result


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_swift_code(swift_code: SwiftCodeCreate, db: Session = Depends(get_db)):
    """
    Add a new SWIFT code entry to the database.
    """
    try:
        result = SwiftCodeService.create_swift_code(db, swift_code.model_dump())
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create SWIFT code: {str(e)}"
        )


@router.delete("/{swift_code}", response_model=MessageResponse)
def delete_swift_code(swift_code: str, db: Session = Depends(get_db)):
    """
    Delete a SWIFT code entry from the database.
    """
    try:
        result = SwiftCodeService.delete_swift_code(db, swift_code)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete SWIFT code: {str(e)}"
        )