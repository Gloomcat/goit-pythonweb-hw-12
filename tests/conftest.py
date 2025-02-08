import asyncio
import pytest

from datetime import timedelta, datetime

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.database.models import Base, User, Contact, UserRole
from src.database.db import get_db
from src.services.auth import create_access_token, Hash

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "12345678",
    "role": "admin",
    "avatar": "https://twitter.com/gravatar",
}


test_user_register = {
    "username": "testuserregister",
    "email": "testuserregister@example.com",
    "password": "12345678",
    "role": "user",
    "avatar": "https://twitter.com/gravatar",
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                role=test_user["role"],
                confirmed=True,
                avatar="https://twitter.com/gravatar",
            )
            session.add(current_user)
            await session.commit()

            # Create sample contacts with different birth dates
            today = datetime.now().date().replace(year=2000)
            contacts = [
                Contact(
                    first_name="Alice",
                    last_name="Smith",
                    email="alice@example.com",
                    phone="tel:+380-68-123-4861",
                    date_of_birth=today + timedelta(days=3),  # ✅ Birthday in 3 days
                    user_id=current_user.id,
                ),
                Contact(
                    first_name="Bob",
                    last_name="Brown",
                    email="bob@example.com",
                    phone="tel:+380-66-123-4862",
                    date_of_birth=today
                    + timedelta(days=10),  # ❌ Birthday in 10 days (outside range)
                    user_id=current_user.id,
                ),
                Contact(
                    first_name="Charlie",
                    last_name="Johnson",
                    email="charlie@example.com",
                    phone="tel:+380-67-123-4863",
                    date_of_birth=today - timedelta(days=5),  # ❌ Birthday 5 days ago
                    user_id=current_user.id,
                ),
                Contact(
                    first_name="Dana",
                    last_name="White",
                    email="dana@example.com",
                    phone="tel:+380-63-123-4864",
                    date_of_birth=today + timedelta(days=6),  # ✅ Birthday in 6 days
                    user_id=current_user.id,
                ),
            ]
            session.add_all(contacts)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture()
def get_token():
    return create_access_token(data={"sub": test_user["username"]})
