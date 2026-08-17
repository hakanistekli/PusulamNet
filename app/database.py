from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
try:
    from app.config import settings
except ModuleNotFoundError:
    try:
        from config import settings
    except ModuleNotFoundError:
        from config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 30}

engine_options = {"connect_args": connect_args, "echo": False}
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_options.update({"pool_pre_ping": True, "pool_recycle": 300})

engine = create_engine(settings.DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
