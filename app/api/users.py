from datetime import datetime 

from fastapi import APIRouter, Depends, Query, status

from app.config import Settings, get_settings
from app.core.errors import InvalidRequest
from app.dependencies import get_now, get_user_repository
from app.repositories.users import UserRepository
from app.schemas.users import UserCreate, UserOut
from app.services.users import list_users, register_user

router = APIRouter(prefix="/users", tags=["users"])

CARD_FILTER_VALUES = {"yes": True, "no": False}


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    users: UserRepository = Depends(get_user_repository),
    now: datetime = Depends(get_now),
    settings: Settings = Depends(get_settings),
) -> UserOut:
    user = register_user(payload, users, now, settings.minimum_age)
    return UserOut.from_user(user)


@router.get("", response_model=list[UserOut])
def get_users(
    credit_card: str | None = Query(default=None, alias="CreditCard"),
    users: UserRepository = Depends(get_user_repository),
) -> list[UserOut]:
    has_card = None
    if credit_card is not None:
        has_card = CARD_FILTER_VALUES.get(credit_card.lower())
        if has_card is None:
            raise InvalidRequest(
                "Request failed validation",
                [{"field": "CreditCard", "problem": "Must be Yes or No"}],
            )
    return [UserOut.from_user(user) for user in list_users(users, has_card)]