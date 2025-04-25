from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from src.database.db import get_db, engine, Base
from src.api.routes import router as swift_router
from src.services.swift_service import SwiftCodeService
from src.database.models import SwiftCode

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_file = os.environ.get("SWIFT_DATA_FILE", "data/swift_codes.csv")

    if os.path.exists(data_file):
        db = next(get_db())
        try:
            db.query(SwiftCode).delete()
            db.commit()
            SwiftCodeService.seed_database(db, data_file)
            print(f"Database seeded with SWIFT codes from {data_file}")
        except Exception as e:
            print(f"Failed to seed database: {str(e)}")

    yield

app = FastAPI(
    title="SWIFT Codes API",
    description="API for managing SWIFT/BIC codes for banks",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(swift_router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "SWIFT Codes API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
