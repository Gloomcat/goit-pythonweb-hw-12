from typing import Annotated, Union
from datetime import date

from pydantic import BaseModel, Field, EmailStr, PastDate
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

ContactNumberType = Annotated[Union[str, PhoneNumber], PhoneNumberValidator()]


class ContactModel(BaseModel):
    """
    Base model for representing a contact.

    Attributes:
        first_name (str | None): The first name of the contact (min: 2, max: 25 characters).
        last_name (str | None): The last name of the contact.
        email (EmailStr | None): The email address of the contact.
        phone (ContactNumberType | None): The contact's phone number (validated format).
        date_of_birth (PastDate | None): The contact's date of birth (must be in the past and after 1900-01-01).
    """

    first_name: str | None = Field(None, min_length=2, max_length=25)
    last_name: str | None
    email: EmailStr | None
    phone: ContactNumberType | None
    date_of_birth: PastDate | None = Field(None, ge=date(1900, 1, 1))


class ContactCreateModel(ContactModel):
    """
    Model for creating a new contact.

    Inherits all attributes from `ContactModel` but enforces `first_name` and `phone` as required.

    Attributes:
        first_name (str): The first name of the contact (required).
        phone (ContactNumberType): The contact's phone number (required, validated format).
    """

    first_name: str
    phone: ContactNumberType


class ContactResponseModel(ContactModel):
    """
    Model for returning contact details in API responses.

    Inherits from `ContactModel` and includes an additional `id` attribute.

    Attributes:
        id (int): The unique identifier of the contact.
    """

    id: int
