from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from .config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.tidb_connection_string,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_size=10,       # Number of connections to keep open
    max_overflow=20,    # Max number of connections to create if pool is full
    connect_args={
        'connect_timeout': 10,  # 10 second timeout
        'sql_mode': 'TRADITIONAL',  # Enable strict mode
    }
)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session.
    Use this in FastAPI path operations to get a DB session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables.
    This should be called during application startup.
    """
    Base.metadata.create_all(bind=engine)
