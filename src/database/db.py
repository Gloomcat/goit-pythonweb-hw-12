import contextlib
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Manages the asynchronous database sessions.

    This class is responsible for creating and maintaining an async SQLAlchemy
    session and engine.

    Attributes:
        _engine (AsyncEngine | None): The SQLAlchemy async engine.
        _session_maker (async_sessionmaker): A session factory for creating async sessions.
    """

    def __init__(self, url: str):
        """
        Initializes the database session manager.

        Args:
            url (str): The database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provides an asynchronous database session.

        This method creates a new session, ensures rollback on errors,
        and closes the session upon completion.

        Yields:
            AsyncSession: An active SQLAlchemy session.

        Raises:
            Exception: If the session manager is not initialized.
            SQLAlchemyError: If an error occurs during the session.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


# Global database session manager instance
sessionmanager = DatabaseSessionManager(settings.DB_URL)

# Base model for SQLAlchemy ORM models
Base = declarative_base()


async def get_db():
    """
    Dependency function to retrieve a database session.

    This function provides an async session for use in FastAPI dependency injection.

    Yields:
        AsyncSession: An active SQLAlchemy session.
    """
    async with sessionmanager.session() as session:
        yield session
