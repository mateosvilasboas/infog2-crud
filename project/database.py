from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from project.config import settings

engine = create_async_engine(settings.DB_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
