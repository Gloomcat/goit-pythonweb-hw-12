from datetime import timedelta
from faker import Faker
from faker.providers.phone_number import Provider
from random import randint, choice
from typing import List

from sqlalchemy import select, func, Interval
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas.contacts import ContactCreateModel, ContactModel
from src.schemas.users import UserDetail


class UAPhoneNumberProvider(Provider):
    """
    Custom Faker provider for generating Ukrainian phone numbers.
    """

    OP_CODES = ["77", "93", "66", "73", "63", "67", "50"]

    def get_op_code(self):
        """
        Retrieves a random Ukrainian mobile operator code.

        Returns:
            str: A random mobile operator code.
        """
        return choice(self.OP_CODES)

    def ua_phone_number(self) -> str:
        """
        Generates a fake Ukrainian phone number.

        Returns:
            str: A valid Ukrainian phone number.
        """
        return f"+380{self.get_op_code()}{randint(1000000, 9999999)}"


fake = Faker(locale="uk_UA")
fake.add_provider(UAPhoneNumberProvider)


class ContactRepository:
    """
    Repository class for managing contacts in the database.

    Attributes:
        db (AsyncSession): The async database session.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the ContactRepository with a database session.

        Args:
            session (AsyncSession): The async database session.
        """
        self.db = session

    async def get_contacts(
        self,
        user: UserDetail,
        skip: int | None = None,
        limit: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        birthdays: bool = False,
    ) -> List[Contact]:
        """
        Retrieves a list of contacts with optional filtering.

        Args:
            user (UserDetail): The authenticated user.
            skip (int, optional): Number of records to skip.
            limit (int, optional): Maximum number of records to return.
            first_name (str, optional): Filter by first name.
            last_name (str, optional): Filter by last name.
            email (str, optional): Filter by email.
            birthdays (bool, optional): If True, fetch contacts with birthdays in the next 7 days.

        Returns:
            List[Contact]: A list of contacts.
        """
        stmt = select(Contact).filter_by(user=user)
        if birthdays:
            stmt = stmt.filter(self._has_birthday_next_days(Contact.date_of_birth, 7))
        else:
            if skip:
                stmt = stmt.offset(skip)
            if limit:
                stmt = stmt.limit(limit)
            if first_name:
                stmt = stmt.where(Contact.first_name == first_name)
            if last_name:
                stmt = stmt.where(Contact.last_name == last_name)
            if email:
                stmt = stmt.where(Contact.email == email)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(
        self, user: UserDetail, contact_id: int
    ) -> Contact | None:
        """
        Retrieves a contact by its ID.

        Args:
            user (UserDetail): The authenticated user.
            contact_id (int): The ID of the contact.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        stmt = select(Contact).filter_by(user=user, id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(
        self, user: UserDetail, body: ContactCreateModel
    ) -> Contact:
        """
        Creates a new contact.

        Args:
            user (UserDetail): The authenticated user.
            body (ContactCreateModel): The contact data.

        Returns:
            Contact: The created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def seed_contacts(self, user: UserDetail, count: int) -> None:
        """
        Seeds the database with fake contacts.

        Args:
            user (UserDetail): The authenticated user.
            count (int): The number of fake contacts to create.
        """
        for _ in range(count):
            contact_model = self._create_fake_contact()
            contact = Contact(**contact_model.model_dump(exclude_unset=True), user=user)
            self.db.add(contact)
        await self.db.commit()

    async def update_contact(
        self, user: UserDetail, contact_id: int, body: ContactModel
    ) -> Contact | None:
        """
        Updates an existing contact.

        Args:
            user (UserDetail): The authenticated user.
            contact_id (int): The ID of the contact.
            body (ContactModel): The updated contact data.

        Returns:
            Contact | None: The updated contact if successful, otherwise None.
        """
        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            update_data = body.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, user: UserDetail, contact_id: int) -> Contact | None:
        """
        Deletes a contact by its ID.

        Args:
            user (UserDetail): The authenticated user.
            contact_id (int): The ID of the contact.

        Returns:
            Contact | None: The deleted contact if successful, otherwise None.
        """
        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    def _age_years_at(self, date_col, next_days: int = 0):
        """
        Calculates the age in years at a given future date.

        Args:
            date_col (Column): The column containing the date of birth.
            next_days (int, optional): The number of days ahead for age calculation.

        Returns:
            Column: A SQL expression for age calculation.
        """
        stmt = func.age(
            (date_col - func.cast(timedelta(next_days), Interval))
            if next_days != 0
            else date_col
        )
        stmt = func.date_part("year", stmt)
        return stmt

    def _has_birthday_next_days(self, date_col, next_days: int = 0):
        """
        Determines if a contact has a birthday in the next specified days.

        Args:
            date_col (Column): The column containing the date of birth.
            next_days (int, optional): Number of days ahead to check for birthdays.

        Returns:
            Column: A SQL expression evaluating whether the birthday falls within the range.
        """
        return self._age_years_at(date_col, next_days) > self._age_years_at(date_col)

    def _create_fake_contact(self) -> ContactModel:
        """
        Generates a fake contact using Faker.

        Returns:
            ContactModel: A fake contact model.
        """
        return ContactModel(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.unique.ua_phone_number(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=90),
        )
