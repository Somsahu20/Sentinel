import psycopg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from ..configs.configs import settings

DATABASE_URL = f'postgresql+psycopg://{settings.db_user}:{settings.password}@{settings.db_host}/{settings.db_name}'

engine = create_async_engine(url=DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()