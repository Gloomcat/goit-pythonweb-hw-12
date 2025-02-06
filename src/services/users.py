from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository
from src.schemas.users import UserCreate


class UserService:
    """
    Service class for managing user operations.

    This class provides an abstraction layer between the API and the user repository.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService with a database session.

        Args:
            db (AsyncSession): The async database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user.

        Args:
            body (UserCreate): The user registration data.

        Returns:
            User: The newly created user.
        """
        return await self.repository.create_user(body)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): The unique ID of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieves a user by their email.

        Args:
            email (str): The email address of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Updates the avatar URL of a user.

        Args:
            email (str): The email of the user.
            url (str): The new avatar URL.

        Returns:
            User: The updated user with the new avatar URL.
        """
        return await self.repository.update_avatar_url(email, url)

    async def confirmed_email(self, email: str):
        """
        Confirms the user's email address.

        Args:
            email (str): The email of the user to confirm.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)
