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
    OP_CODES = ["77", "93", "66", "73", "63", "67", "50"]

    def get_op_code(self):
        return choice(self.OP_CODES)

    def ua_phone_number(self) -> str:
        return f"+380{self.get_op_code()}{randint(1000000, 9999999)}"


fake = Faker(locale="uk_UA")
fake.add_provider(UAPhoneNumberProvider)


class ContactRepository:
    def __init__(self, session: AsyncSession):
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
        stmt = select(Contact).filter_by(user=user, id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(
        self, user: UserDetail, body: ContactCreateModel
    ) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def seed_contacts(self, user: UserDetail, count: int) -> None:
        for _ in range(count):
            contact_model = self._create_fake_contact()
            contact = Contact(**contact_model.model_dump(exclude_unset=True), user=user)
            self.db.add(contact)
        await self.db.commit()

    async def update_contact(
        self, user: UserDetail, contact_id: int, body: ContactModel
    ) -> Contact | None:
        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            update_data = body.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, user: UserDetail, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    def _age_years_at(self, date_col, next_days: int = 0):
        stmt = func.age(
            (date_col - func.cast(timedelta(next_days), Interval))
            if next_days != 0
            else date_col
        )
        stmt = func.date_part("year", stmt)
        return stmt

    def _has_birthday_next_days(self, date_col, next_days: int = 0):
        return self._age_years_at(date_col, next_days) > self._age_years_at(date_col)

    def _create_fake_contact(self) -> ContactModel:
        return ContactModel(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.unique.ua_phone_number(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=90),
        )
