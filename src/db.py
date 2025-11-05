import asyncio
import contextlib
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from schema_models import Base
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine, AsyncEngine
from core.config import config
from typing import Any


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):  # pyright: ignore[reportExplicitAny, reportCallInDefaultInitializer]
        self._engine: AsyncEngine | None = create_async_engine(host, **engine_kwargs)
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = (
            async_sessionmaker(
                bind=self._engine, expire_on_commit=False, autoflush=False
            )
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized.")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized.")

        async with self._engine.begin() as connection:
            yield connection

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized.")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager: DatabaseSessionManager = DatabaseSessionManager(
    config.DATABASE_URL, {"echo": config.ECHO_SQL}
)


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session


async def create_tables() -> None:
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)


if __name__ == "__main__":
    action: str = input("Type CREATE to create all tables or DROP to drop all tables.")
    if action == "CREATE":
        asyncio.run(create_tables())
    elif action == "DROP":
        asyncio.run(drop_tables())
