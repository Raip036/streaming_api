from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic.alias_generators import to_camel

from app.core.security import MAX_PASSWORD_BYTES, mask_card
from app.models import User

USERNAME_PATTERN = r"^[A-Za-z0-9]+$"
CARD_PATTERN = r"^[0-9]{16}$"


class UserCreate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    username: str = Field(min_length=1, max_length=30, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=8)
    email: EmailStr
    dob: date
    credit_card_number: str | None = Field(default=None, pattern=CARD_PATTERN)

    @field_validator("password")
    @classmethod
    def password_is_strong_enough(cls, value: str) -> str:
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError(f"Must be at most {MAX_PASSWORD_BYTES} bytes long")

        if not any(character.isupper() for character in value):
            raise ValueError("Must contain at least one upper-case letter")

        if not any(character.isdigit() for character in value):
            raise ValueError("Must contain at least one number")
        return value

    @field_validator("dob", mode="before")
    @classmethod
    def dob_is_an_iso_date(cls, value: object) -> date:
        if not isinstance(value, str):
            raise ValueError("Must be a date in ISO 8601 format, for example 1998-04-12")
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            raise ValueError("Must be a date in ISO 8601 format, for example 1998-04-12") from None
        if parsed > date.today():
            raise ValueError("Must not be in the future")
        return parsed


class UserOut(BaseModel):
    """A user as shown in responses: no password, and the card masked."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    username: str
    email: EmailStr
    dob: date
    credit_card: str | None
    registered_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserOut":
        return cls(
            username=user.username,
            email=user.email,
            dob=user.dob,
            credit_card=mask_card(user.credit_card_number) if user.credit_card_number else None,
            registered_at=user.registered_at,
        )
