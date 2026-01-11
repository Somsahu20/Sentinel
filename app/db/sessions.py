import psycopg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from ..configs.configs import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = f'postgresql+psycopg://{settings.db_user}:{settings.password}@{settings.db_host}/{settings.db_name}'

engine = create_async_engine(url=DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)


sync_engine = create_engine(url=DATABASE_URL, echo=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autoflush=False, expire_on_commit=True)

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()