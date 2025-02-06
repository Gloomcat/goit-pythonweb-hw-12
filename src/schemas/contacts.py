from typing import Annotated, Union

from datetime import date

from pydantic import BaseModel, Field, EmailStr, PastDate
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

ContactNumberType = Annotated[Union[str, PhoneNumber], PhoneNumberValidator()]


class ContactModel(BaseModel):
    first_name: str | None = Field(None, min_length=2, max_length=25)
    last_name: str | None
    email: EmailStr | None
    phone: ContactNumberType | None
    date_of_birth: PastDate | None = Field(None, ge=date(1900, 1, 1))


class ContactCreateModel(ContactModel):
    first_name: str
    phone: ContactNumberType


class ContactResponseModel(ContactModel):
    id: int
