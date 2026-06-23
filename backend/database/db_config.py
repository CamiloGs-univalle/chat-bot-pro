from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    "postgresql://postgres:postgres123@localhost:5432/whatsapp_bot"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)