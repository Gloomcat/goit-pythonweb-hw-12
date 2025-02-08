import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreateModel, ContactModel
from src.database.models import Contact
from src.database.models import User


@pytest.fixture
def mock_db_session():
    """
    Provides a mock database session using AsyncMock.
    """
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_repository(mock_db_session):
    """
    Provides an instance of ContactRepository with a mocked session.
    """
    return ContactRepository(mock_db_session)


@pytest.fixture
def sample_user():
    """
    Provides a sample user detail for testing.
    """
    return User(id=1, username="testuser", email="test@example.com", avatar=None)


@pytest.fixture
def sample_contact_data():
    """
    Provides a sample contact creation model for testing.
    """
    return ContactCreateModel(
        first_name="John",
        last_name="Doe",
        email="johndoe@example.com",
        phone="+380671234567",
        date_of_birth="1990-01-01",
    )


@pytest.mark.asyncio
async def test_create_contact(
    contact_repository, sample_user, sample_contact_data, mock_db_session
):
    # Mock database behavior
    result = await contact_repository.create_contact(sample_user, sample_contact_data)

    # Assertions
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()
    assert isinstance(result, Contact)
    assert result.first_name == "John"


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, sample_user, mock_db_session):
    mock_contacts = [
        Contact(
            id=1,
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            phone="+380671234568",
            user=sample_user,
        ),
        Contact(
            id=2,
            first_name="Bob",
            last_name="Brown",
            email="bob@example.com",
            phone="+380671234569",
            user=sample_user,
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_contacts
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.get_contacts(sample_user)

    # Assertions
    assert len(result) == 2
    assert result[0].first_name == "Alice"
    assert result[1].first_name == "Bob"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, sample_user, mock_db_session):
    mock_contact = Contact(
        id=1,
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="+380671234568",
        user=sample_user,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_contact
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.get_contact_by_id(sample_user, 1)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.first_name == "Alice"


@pytest.mark.asyncio
async def test_update_contact(contact_repository, sample_user, mock_db_session):
    mock_contact = Contact(
        id=1,
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="+380671234568",
        user=sample_user,
    )
    updated_data = ContactModel(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="+380671234868",
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_contact
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(sample_user, 1, updated_data)

    # Assertions
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()
    assert result.phone == "tel:+380-67-123-4868"


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, sample_user, mock_db_session):
    mock_contact = Contact(
        id=1,
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="+380671234568",
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_contact
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(sample_user, 1)

    # Assertions
    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()
    assert result.id == 1


@pytest.mark.asyncio
async def test_create_contact_with_duplicate_values(
    contact_repository, sample_user, sample_contact_data, mock_db_session
):
    mock_db_session.commit.side_effect = IntegrityError("Duplicate entry", {}, None)

    with pytest.raises(IntegrityError):
        await contact_repository.create_contact(sample_user, sample_contact_data)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_nonexistent_contact_by_id(
    contact_repository, sample_user, mock_db_session
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.get_contact_by_id(sample_user, 999)

    assert result is None


@pytest.mark.asyncio
async def test_update_nonexistent_contact(
    contact_repository, sample_user, mock_db_session
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    updated_data = ContactModel(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="+380671234868",
    )
    result = await contact_repository.update_contact(sample_user, 999, updated_data)

    assert result is None
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_remove_nonexistent_contact(
    contact_repository, sample_user, mock_db_session
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(sample_user, 999)

    assert result is None
    mock_db_session.commit.assert_not_called()
