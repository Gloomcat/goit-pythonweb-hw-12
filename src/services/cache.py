import json

from typing import Optional

import redis.asyncio as redis  # Note the `asyncio` submodule

from src.database.models import User
from src.conf.config import settings


redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


async def update_cached_current_user(user: User) -> None:
    """
    Updates or adds the current user to the Redis cache.

    This function serializes the user data and stores it in Redis with a key
    based on the user's ID. The cache entry expires after a specified time
    (determined by `JWT_EXPIRATION_MINUTES` from the settings).

    Args:
        user (User): The user object to be cached.

    Returns:
        None
    """
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "avatar": user.avatar,
        "confirmed": user.confirmed,
    }

    await redis_client.set(f"user:{user.username}", json.dumps(user_data), ex=settings.JWT_EXPIRATION_MINUTES * 60)

async def get_cached_current_user(username: str) -> Optional[User]:
    """
    Retrieves the current user from the Redis cache using the username.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        Optional[User]: The cached user object if found, otherwise None.
    """
    user_data = await redis_client.get(f"user:{username}")

    if user_data:
        try:
            data = json.loads(user_data)
            return User(
                id=data.get("id"),
                username=data.get("username"),
                email=data.get("email"),
                role=data.get("role"),
                avatar=data.get("avatar"),
                confirmed=data.get("confirmed", False),
            )
        except json.JSONDecodeError as e:
            print(f"Failed to decode user data from cache: {e}")
            return None

    return None