from datetime import UTC, datetime

from app.repositories.payments import InMemoryPaymentRepository, PaymentRepository
from app.repositories.users import InMemoryUserRepository, UserRepository

_user_repository = InMemoryUserRepository()
_payment_repository = InMemoryPaymentRepository()


def get_user_repository() -> UserRepository:
    return _user_repository

def get_payment_repository() -> PaymentRepository:
    return _payment_repository

def get_now() -> datetime:
    return datetime.now(UTC)