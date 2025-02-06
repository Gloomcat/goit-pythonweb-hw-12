from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreateModel, ContactModel
from src.schemas.users import UserDetail


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, user: UserDetail, body: ContactCreateModel):
        return await self.repository.create_contact(user, body)

    async def seed_contacts(self, user: UserDetail, count: int):
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
        return await self.repository.get_contacts(
            user, skip, limit, first_name, last_name, email, birthdays
        )

    async def get_contact(self, user: UserDetail, contact_id: int):
        return await self.repository.get_contact_by_id(user, contact_id)

    async def update_contact(
        self, user: UserDetail, contact_id: int, body: ContactModel
    ):
        return await self.repository.update_contact(user, contact_id, body)

    async def remove_contact(self, user: UserDetail, contact_id: int):
        return await self.repository.remove_contact(user, contact_id)
