from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.users import UserService
from src.schemas.users import UserDetail, UserCreate, Token, RequestEmail
from src.services.auth import create_access_token, get_email_from_token, Hash
from src.services.email import send_email


router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.post("/login", response_model=Token, status_code=status.HTTP_201_CREATED)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user and returns an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The user's login credentials.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If authentication fails or email is not verified.
    """
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
    """
    Registers a new user and sends a confirmation email.

    Args:
        user_data (UserCreate): The new user's details.
        background_tasks (BackgroundTasks): Background tasks for sending emails.
        request (Request): The incoming request.
        db (AsyncSession): Database session dependency.

    Returns:
        UserDetail: The created user object.

    Raises:
        HTTPException: If the email or username is already taken.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the email already exists.",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the username already exists.",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    try:
        g = Gravatar(user_data.email)
        user_data.avatar = g.get_image()
    except Exception:
        pass

    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url, "Confirm your email", "verify_email.html"
    )
    return new_user


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirms a user's email using a verification token.

    Args:
        token (str): The email verification token.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating the verification status.

    Raises:
        HTTPException: If verification fails.
    """
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

@router.post(
    "/forgot_password", status_code=status.HTTP_202_ACCEPTED
)
async def forgot_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Sends a password reset email on user request.

    Args:
        body (RequestEmail): The email address of the user.
        background_tasks (BackgroundTasks): Background tasks for sending emails.
        request (Request): The incoming request.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating request accepted.
    """
    user_service = UserService(db)

    user = await user_service.get_user_by_email(body.email)
    if user and user.confirmed:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url, "Password reset", "password_reset.html"
        )

    return { "message": "Password reset requested." }


@router.get("/reset_password/{token}", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    """
    Serves the password reset form for the given token.

    This endpoint renders the password reset form for the token if the user exists and is confirmed.

    Args:
        request (Request): The incoming request object.
        token (str): The password reset token.
        db (AsyncSession): Database session dependency.

    Returns:
        TemplateResponse: The password reset form with the token included in the context.

    Raises:
        HTTPException: If the user is not found or not confirmed.
    """
    email = await get_email_from_token(token)

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None or not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    return templates.TemplateResponse("password_reset_form.html", {"request": request, "token": token})



@router.post("/reset_password/{token}", status_code=status.HTTP_201_CREATED
)
async def reset_password(token: str, password: str = Form(),  db: AsyncSession = Depends(get_db)):
    """
    Resets the user's password.

    Args:
        token (str): Password reset token.
        password (str): New password from form data.
        db (AsyncSession): Database session.

    Returns:
        dict: Message about successfull password reset.

    Raises:
        HTTPException: If verification fails or the user is not found.
    """
    email = await get_email_from_token(token)

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None or not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    hashed_password = Hash().get_password_hash(password)
    await user_service.update_password(email, hashed_password)
    return {"message": "Password reset successfully"}