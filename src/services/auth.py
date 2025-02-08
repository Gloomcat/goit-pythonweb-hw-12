from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import encode as jwt_encode, decode as jwt_decode
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, UserRole
from src.conf.config import settings
from src.services.users import UserService
from src.services.cache import get_cached_current_user


class Hash:
    """
    Provides password hashing and verification using bcrypt.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies that a given plaintext password matches the hashed password.

        Args:
            plain_password (str): The plaintext password.
            hashed_password (str): The stored hashed password.

        Returns:
            bool: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hashes a plaintext password.

        Args:
            password (str): The plaintext password.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Creates a new JWT access token.

    Args:
        data (dict): The payload to encode in the token.
        expires_delta (Optional[int], optional): The expiration time in minutes. Defaults to settings.JWT_EXPIRATION_MINUTES.

    Returns:
        str: The generated JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt_encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_email_token(data: dict) -> str:
    """
    Creates a JWT token for email verification.

    Args:
        data (dict): The payload to encode in the token.

    Returns:
        str: The generated JWT email verification token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt_encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str) -> str:
    """
    Extracts the email address from a JWT token.

    Args:
        token (str): The JWT token.

    Returns:
        str: The extracted email address.

    Raises:
        HTTPException: If the token is invalid or cannot be decoded.
    """
    try:
        payload = jwt_decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email verification",
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Retrieves the current authenticated user based on the JWT token.

    Args:
        token (str): The JWT token extracted from the request.
        db (Session): The database session.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt_decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    cached_user = await get_cached_current_user(username)
    if cached_user:
        return cached_user

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Insufficient access rights")
    return current_user
