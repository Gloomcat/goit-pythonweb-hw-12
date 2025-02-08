from enum import Enum

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserDetail(BaseModel):
    """
    Represents detailed user information.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        avatar (str | None): The URL of the user's avatar (optional).
    """

    id: int
    username: str
    email: str
    role: UserRole
    avatar: str | None


class UserCreate(BaseModel):
    """
    Represents a request model for user registration.

    Attributes:
        username (str): The desired username for the new user.
        email (EmailStr): The email address of the user.
        password (str): The password for the user account.
    """

    username: str
    email: EmailStr
    password: str
    role: UserRole


class Token(BaseModel):
    """
    Represents an authentication token response.

    Attributes:
        access_token (str): The generated access token.
        token_type (str): The type of token (e.g., "bearer").
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Represents a request model for email-based actions.

    Attributes:
        email (EmailStr): The email address for the request.
    """

    email: EmailStr
