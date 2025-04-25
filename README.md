# SWIFT Codes API

## Overview
The SWIFT Codes API is a FastAPI-based application designed to manage and query SWIFT/BIC codes for banks. It provides endpoints to retrieve, create, and delete SWIFT code entries, with support for headquarters and branch associations. The application uses a PostgreSQL database and includes automated testing and Docker deployment workflows.

## Features
- **Retrieve SWIFT Codes**: Query individual SWIFT codes, including headquarters with associated branches.
- **Country-based Queries**: Fetch all SWIFT codes for a specific country using ISO2 codes.
- **Create/Delete Entries**: Add new SWIFT codes or remove existing ones.
- **Database Seeding**: Automatically populate the database from a CSV file during startup.
- **CI/CD Pipelines**: GitHub Actions workflows for testing and Docker image building/publishing.
- **Test Coverage**: Unit tests with coverage reporting using pytest and Codecov.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Testing**: Pytest, pytest-cov
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Dependencies**: Managed via requirements.txt

## Prerequisites
- Docker
- Docker Compose

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/kacpersmaga/swift-codes-api.git
   cd swift-codes-api
   ```

2. **Start the Application**:
   ```bash
   docker-compose up -d
   ```

3. **Access the API**:
   The API will be available at `http://localhost:8080`.

4. **Check if the API is Running**:
   ```bash
   curl http://localhost:8080
   ```

## API Endpoints
- **Health Check**: `GET /`
  - Returns: `{ "status": "ok", "message": "SWIFT Codes API is running" }`
- **Get SWIFT Code**: `GET /v1/swift-codes/{swift_code}`
  - Returns details of a SWIFT code, including branches if it's a headquarters.
- **Get Country SWIFT Codes**: `GET /v1/swift-codes/country/{country_iso2}`
  - Returns all SWIFT codes for a given country (ISO2 code).
- **Create SWIFT Code**: `POST /v1/swift-codes`
  - Body: JSON with `swiftCode`, `bankName`, `address`, `countryISO2`, `countryName`, `isHeadquarter`.
  - Returns: Confirmation message.
- **Delete SWIFT Code**: `DELETE /v1/swift-codes/{swift_code}`
  - Returns: Confirmation message.

Explore the API documentation at `http://localhost:8080/docs` for detailed endpoint information.

## Database Seeding
The application automatically seeds the database with SWIFT codes from a CSV file specified in `SWIFT_DATA_FILE`. The CSV must contain:
- `country_iso2_code`
- `swift_code`
- `name`
- `address`
- `country_name`

Ensure the file exists and is correctly formatted before running the application.

## Running Tests
1. Ensure the PostgreSQL service is available (configured in `test.yml`).
2. Run tests using one of the following commands:
   - With Docker:
     ```bash
     docker-compose -f docker-compose.yml run api pytest tests/ -v
     ```
   - Locally (with Python environment set up):
     ```bash
     python -m pytest tests/ -v
     ```

Test results and coverage are reported to Codecov via the GitHub Actions workflow.

## Docker Deployment
The application is deployed using Docker. The GitHub Actions workflow (`docker-build.yml`) automates building and pushing the Docker image to Docker Hub on pushes to the `master` branch.

## CI/CD Workflows
- **Testing (`test.yml`)**:
  - Runs on all push and pull request events.
  - Sets up PostgreSQL, installs dependencies, runs unit tests, and uploads coverage to Codecov.
- **Docker Build (`docker-build.yml`)**:
  - Runs on push and pull requests to the `master` branch.
  - Builds and pushes the Docker image to Docker Hub (for pushes only).

## Project Structure
```
swift-codes-api/
├── src/
│   ├── api/
│   │   └── routes.py          # API route definitions
│   ├── database/
│   │   ├── db.py             # Database configuration and session management
│   │   └── models.py         # SQLAlchemy models
│   ├── repositories/
│   │   └── swift_repository.py # Database operations
│   ├── schemas/
│   │   └── swift_code.py     # Pydantic models for validation
│   ├── services/
│   │   └── swift_service.py  # Business logic
│   ├── utils/
│   │   └── parser.py         # CSV parsing for database seeding
│   └── main.py               # Application entry point
├── tests/                    # Unit tests
├── data/                     # CSV files for seeding (e.g., swift_codes.csv)
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── docker-build.yml          # GitHub Actions workflow for Docker
├── test.yml                  # GitHub Actions workflow for testing
└── Dockerfile                # Docker configuration
```

## Author
**Kacper Smaga**  
Email: kacper.smaga@onet.pl  
GitHub: [kacpersmaga](https://github.com/kacpersmaga)
