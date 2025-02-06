from datetime import date
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Date

from src.database.db import Base


class User(Base):
    """
    Represents a user in the application.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): The user's username (must be unique).
        hashed_password (str): The user's password, stored as a hash.
        email (str, optional): The user's email address (must be unique).
        avatar (str, optional): URL to the user's avatar image.
        confirmed (bool): Whether the user's email has been verified.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)


class Contact(Base):
    """
    Represents a contact in the application.

    Attributes:
        id (int): Unique identifier for the contact.
        first_name (str): The first name of the contact.
        last_name (str, optional): The last name of the contact.
        email (str, optional): The email address of the contact (must be unique).
        phone (str): The phone number of the contact (must be unique).
        date_of_birth (date, optional): The contact's date of birth.
        user_id (int, optional): The ID of the user who owns the contact.
        user (User): Relationship to the `User` model.
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    phone: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")
