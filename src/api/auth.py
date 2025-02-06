from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.users import UserService
from src.schemas.users import UserDetail, UserCreate, Token, RequestEmail
from src.services.auth import create_access_token, get_email_from_token, Hash
from src.services.email import send_email


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token, status_code=status.HTTP_201_CREATED)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email address is not verified",
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register", response_model=UserDetail, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the email is already exist.",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the username is already exist.",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    try:
        g = Gravatar(user_data.email)
        user_data.avatar = g.get_image()
    except Exception as e:
        pass

    new_user = await user_service.create_user(user_data)
    print(request.base_url)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already verified"}
    await user_service.confirmed_email(email)
    return {"message": "Your email is verified"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Your email is already verified"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for verification"}
