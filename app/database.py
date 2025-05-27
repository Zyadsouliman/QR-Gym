from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings
import logging

settings = get_settings()

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://root:Zyad%401755@localhost:3307/gymqrs_qrsdb"

try:
    # Create engine with connection pooling
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,  # Enable connection health checks
        echo=True  # Enable SQL query logging
    )
    
    # Test the connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        logging.info("Successfully connected to the database")
except Exception as e:
    logging.error(f"Failed to connect to the database: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 