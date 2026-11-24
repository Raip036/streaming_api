from dataclasses import dataclass
from datetime import date, datetime 

@dataclass(frozen=True)
class User:
    username: str
    password_hash: str
    email: str
    dob: date
    credit_card_number: str | None
    registered_at: datetime

@dataclass(frozen=True)
class Payment:
    id: str
    credit_card_number: str
    amount: int
    created_at: datetime