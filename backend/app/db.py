from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Note: TiDB is MySQL compatible; use mysql+pymysql in DATABASE_URL
# Example: mysql+pymysql://user:pass@host:4000/dbname?ssl=true
_engine = create_engine(
    settings.database_url or "sqlite:///./dev.db",  # fallback for local dev
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    print(db)
    try:
        yield db
    finally:
        db.close()

