import os
import time
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "swift_codes")
MAX_RETRIES = int(os.getenv("DB_MAX_RETRIES", "5"))
RETRY_DELAY = int(os.getenv("DB_RETRY_DELAY", "2"))

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = None
for attempt in range(MAX_RETRIES):
    try:
        logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{MAX_RETRIES})...")
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"connect_timeout": 10}
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Successfully connected to the database")
        break
    except OperationalError as db_error:
        if attempt < MAX_RETRIES - 1:
            logger.warning(f"Database connection failed: {db_error}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            logger.error(f"Failed to connect to the database after {MAX_RETRIES} attempts: {db_error}")
            raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
