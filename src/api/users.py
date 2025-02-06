from typing import List

from fastapi import APIRouter, HTTPException, status, Request, UploadFile, Depends, File
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.conf.config import settings
from src.schemas.users import UserDetail
from src.services.users import UserService
from src.services.auth import get_current_user
from src.services.upload_file import UploadFileService


router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=UserDetail, description="No more than 5 requests per minute"
)
@limiter.limit("5/minute")
async def me(request: Request, user: UserDetail = Depends(get_current_user)):
    return user


@router.patch("/avatar", response_model=UserDetail)
async def update_user_avatar(
    file: UploadFile = File(),
    user: UserDetail = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
