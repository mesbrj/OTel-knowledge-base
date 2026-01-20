from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import event

from config.settings import settings


class DatabaseManager:
    _engine: AsyncEngine | None = None

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        if cls._engine is None:
            cls._engine = cls._create_engine(settings.ENVIRONMENT)
        return cls._engine

    @classmethod
    def reset_engine(cls) -> None:
        cls._engine = None

    @classmethod
    async def init_db(cls) -> None:
        engine = cls.get_engine()
        if settings.ENVIRONMENT in ["development", "test"]:
            from adapter.sql.models import User, Team, Project, ProjectRole, ProjectUserLink
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)

    @classmethod
    def get_session(cls) -> AsyncSession:
        return AsyncSession(cls.get_engine())

    @classmethod
    async def close_session(cls) -> bool:
        engine = cls.get_engine()
        await engine.dispose()
        cls.reset_engine()
        return True

    @classmethod
    def _create_engine(cls, env: str) -> AsyncEngine:
        if env not in ["development", "test"]:
            connection_string = settings.PSQL_DATABASE_URL
            return create_async_engine(
                connection_string,
                echo = False,
                future = True,
                pool_pre_ping = True,
                pool_size = 20,
                max_overflow = 2,
                pool_timeout = 30,
                pool_recycle = 7200,
            )
        else:
            if env == "development":
                connection_string = settings.DEV_SQLITE_URL
            elif env == "test":
                connection_string = settings.TEST_SQLITE_URL
            else:
                raise ValueError("Invalid ENVIRONMENT value")
            dev_engine = create_async_engine(
                connection_string,
                echo = True if settings.DEBUG_SQLALCHEMY == "True" else False,
                connect_args = {
                    "check_same_thread": False
                },
                future = True,
                pool_pre_ping = True,
            )
            @event.listens_for(dev_engine.sync_engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON;")
                cursor.close()

            return dev_engine
