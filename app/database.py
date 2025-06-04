from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings
import os

settings = get_settings()

# Get database URL from environment variable or use default for local development
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://root:Zyad%401755@localhost:3307/gymqrs_qrsdb"
    # f"mysql+pymysql://root:jakWsTRUFCOHWcsJCffNMBlYMyIEnFeY@interchange.proxy.rlwy.net:17104/railway"

)

# Configure engine with serverless-friendly settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=1,  # Reduced pool size for serverless
    max_overflow=2,  # Reduced overflow for serverless
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=settings.DEBUG,  # Only enable SQL logging in debug mode
    connect_args={
        "connect_timeout": 10  # Add connection timeout
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from .models import Base
    Base.metadata.create_all(bind=engine)

def update_db():
    from .models import Base
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine) 