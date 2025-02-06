from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreateModel, ContactModel
from src.schemas.users import UserDetail


class ContactService:
    """
    Service class for managing contacts.

    This class interacts with the ContactRepository to perform
    CRUD operations on contacts.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the ContactService with a database session.

        Args:
            db (AsyncSession): The async database session.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, user: UserDetail, body: ContactCreateModel):
        """
        Creates a new contact.

        Args:
            user (UserDetail): The authenticated user creating the contact.
            body (ContactCreateModel): The contact data.

        Returns:
            Contact: The newly created contact.
        """
        return await self.repository.create_contact(user, body)

    async def seed_contacts(self, user: UserDetail, count: int):
        """
        Seeds the database with fake contacts.

        Args:
            user (UserDetail): The authenticated user.
            count (int): The number of fake contacts to generate.
        """
        await self.repository.seed_contacts(user, count)

    async def get_contacts(
        self,
        user: UserDetail,
        skip: int | None = None,
        limit: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        birthdays: bool = False,
    ):
        """
        Retrieves a list of contacts with optional filtering.

        Args:
            user (UserDetail): The authenticated user.
            skip (int, optional): The number of records to skip.
            limit (int, optional): The maximum number of records to return.
            first_name (str, optional): Filter by first name.
            last_name (str, optional): Filter by last name.
            email (str, optional): Filter by email.
            birthdays (bool, optional): If True, fetch contacts with upcoming birthdays.

        Returns:
            List[Contact]: A list of matching contacts.
        """
        return await self.repository.get_contacts(
            user, skip, limit, first_name, last_name, email, birthdays
        )

    async def get_contact(self, user: UserDetail, contact_id: int):
        """
        Retrieves a contact by its ID.

        Args:
            user (UserDetail): The authenticated user.
            contact_id (int): The ID of the contact.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        return await self.repository.get_contact_by_id(user, contact_id)

    async def update_contact(
        self, user: UserDetail, contact_id: int, body: ContactModel
    ):
        """
        Updates an existing contact.

        Args:
            user (UserDetail): The authenticated user.
            contact_id (int): The ID of the contact.
            body (ContactModel): The updated contact data.

        Returns:
            Contact | None: The updated contact if successful, otherwise None.
        """
        return await self.repository.update_contact(user, contact_id, body)

    async def remove_contact(self, user: UserDetail, contact_id: int):
        """
        Deletes a contact by its ID.

        Args:
            user (UserDetail): The authenticated user.
            contact_id (int): The ID of the contact.

        Returns:
            Contact | None: The deleted contact if successful, otherwise None.
        """
        return await self.repository.remove_contact(user, contact_id)
