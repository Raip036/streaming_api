from datetime import datetime

from app.core.errors import UnderAge, UsernameTaken
from app.core.rules import is_adult
from app.core.security import hash_password
from app.models import User
from app.repositories.users import UserRepository
from app.schemas.users import UserCreate


def register_user(
    data: UserCreate, users: UserRepository, now: datetime, minimum_age: int = 18
) -> User:
    if not is_adult(data.dob, now.date(), minimum_age):
        raise UnderAge(f"Users must be at least {minimum_age} years old")

    if users.exists(data.username):
        raise UsernameTaken("This username is already registered")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        email=data.email,
        dob=data.dob,
        credit_card_number=data.credit_card_number,
        registered_at=now,
    )

    if not users.add(user):
        raise UsernameTaken("This username is already registered")
    return user


def list_users(users: UserRepository, has_card: bool | None = None) -> list[User]:
    return users.find_all(has_card)
