import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository
from src.database.models import User
from src.schemas.users import UserCreate


@pytest.fixture
def mock_db_session():
    """
    Provides a mock database session using AsyncMock.
    """
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_db_session):
    """
    Provides an instance of UserRepository with a mocked session.
    """
    return UserRepository(mock_db_session)


@pytest.fixture
def sample_user():
    """
    Provides a sample user ORM instance for testing.
    """
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123",
        avatar=None,
        confirmed=False,
    )


@pytest.fixture
def sample_user_data():
    """
    Provides a sample user creation model for testing.
    """
    return UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword",
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, sample_user, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_id(1)

    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, sample_user, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_username("testuser")

    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, sample_user, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_email("test@example.com")

    assert result is not None
    assert result.id == 1
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_create_user(user_repository, sample_user_data, mock_db_session):
    result = await user_repository.create_user(sample_user_data)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()
    assert isinstance(result, User)
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, sample_user, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.update_avatar_url("test@example.com", "http://new-avatar.com")

    assert result.avatar == "http://new-avatar.com"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, sample_user, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    await user_repository.confirmed_email("test@example.com")

    assert sample_user.confirmed is True
    mock_db_session.commit.assert_called_once()
