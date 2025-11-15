from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import pool
from sqlalchemy.orm import declarative_base
from config import BD_URL_POSTGRES

Base = declarative_base()

engine = create_async_engine(
    BD_URL_POSTGRES,
    future=True, 
    echo=False, 
    poolclass=pool.NullPool, 
    )
async_session = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)