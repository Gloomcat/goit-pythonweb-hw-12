import re
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database.db import get_db
from src.schemas.contacts import ContactCreateModel, ContactResponseModel, ContactModel
from src.schemas.users import UserDetail
from src.services.contacts import ContactService
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


def extract_integrity_error_message(error: IntegrityError) -> str:
    """
    Extracts a meaningful error message from an IntegrityError.

    Args:
        error (IntegrityError): The integrity error to parse.

    Returns:
        str: A user-friendly error message.
    """
    error_str = str(error.orig)
    if "duplicate key value" in error_str:
        match = re.search(r"Key \((\w+)\)=\((.*?)\)", error_str)
        if match:
            column_name, value = match.groups()
            return f"The value '{value}' for '{column_name}' is already taken. Please use another one."

    return "A database integrity error occurred. Please check your input."


@router.get("/", response_model=List[ContactResponseModel])
async def read_contacts(
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: UserDetail = Depends(get_current_user),
):
    """
    Retrieves a list of contacts based on optional filters.

    Args:
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to return.
        first_name (str, optional): Filter contacts by first name.
        last_name (str, optional): Filter contacts by last name.
        email (str, optional): Filter contacts by email.
        db (AsyncSession): Database session dependency.
        user (UserDetail): The authenticated user.

    Returns:
        List[ContactResponseModel]: A list of contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        user, skip, limit, first_name, last_name, email
    )
    return contacts


@router.get(
    "/birthdays",
    response_model=List[ContactResponseModel],
    description="Returns contacts with birthdays in the next 7 days.",
)
async def read_contacts_with_birthdays(
    db: AsyncSession = Depends(get_db), user: UserDetail = Depends(get_current_user)
):
    """
    Retrieves contacts with upcoming birthdays within the next 7 days.

    Args:
        db (AsyncSession): Database session dependency.
        user (UserDetail): The authenticated user.

    Returns:
        List[ContactResponseModel]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(user, birthdays=True)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponseModel)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserDetail = Depends(get_current_user),
):
    """
    Retrieves a contact by its ID.

    Args:
        contact_id (int): The ID of the contact.
        db (AsyncSession): Database session dependency.
        user (UserDetail): The authenticated user.

    Returns:
        ContactResponseModel: The requested contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(user, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_contacts(
    count: int = Query(default=100),
    db: AsyncSession = Depends(get_db),
    user: UserDetail = Depends(get_current_user),
):
    """
    Seeds the database with random contact entries.

    Args:
        count (int): The number of contacts to create.
        db (AsyncSession): Database session dependency.
        user (UserDetail): The authenticated user.

    Returns:
        dict: A message indicating the number of contacts created.

    Raises:
        HTTPException: If a database integrity error occurs.
    """
    contact_service = ContactService(db)
    try:
        await contact_service.seed_contacts(user, count)
        return {"message": f"{count} contacts created successfully"}
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=extract_integrity_error_message(e),
        )


@router.post(
    "/", response_model=ContactResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_contact(
    body: ContactCreateModel,
    db: AsyncSession = Depends(get_db),
    user: UserDetail = Depends(get_current_user),
):
    """
    Creates a new contact.

    Args:
        body (ContactCreateModel): The details of the contact to create.
        db (AsyncSession): Database session dependency.
        user (UserDetail): The authenticated user.

    Returns:
        ContactResponseModel: The created contact.

    Raises:
        HTTPException: If a database integrity error occurs.
    """
    contact_service = ContactService(db)
    try:
        return await contact_service.create_contact(user, body)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=extract_integrity_error_message(e),
        )


@router.put("/{contact_id}", response_model=ContactResponseModel)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserDetail = Depends(get_current_user),
):
    """
    Updates an existing contact.

    Args:
        body (ContactModel): The updated contact details.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): Database session dependency.
        user (UserDetail): The authenticated user.

    Returns:
        ContactResponseModel: The updated contact.

    Raises:
        HTTPException: If the contact is not found or a database integrity error occurs.
    """
    contact_service = ContactService(db)
    try:
        contact = await contact_service.update_contact(user, contact_id, body)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=extract_integrity_error_message(e),
        )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponseModel)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserDetail = Depends(get_current_user),
):
    """
    Deletes a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): Database session dependency.
        user (UserDetail): The authenticated user.

    Returns:
        ContactResponseModel: The deleted contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(user, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
