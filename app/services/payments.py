from datetime import datetime
from uuid import uuid4

from app.core.errors import CardNotRegistered
from app.models import Payment
from app.repositories.payments import PaymentRepository
from app.repositories.users import UserRepository
from app.schemas.payments import PaymentCreate


def make_payment(
    data: PaymentCreate, users: UserRepository, payments: PaymentRepository, now: datetime
) -> Payment:
    if not users.card_exists(data.credit_card_number):
        raise CardNotRegistered("This credit card is not registered to any user")

    payment = Payment(
        id=str(uuid4()),
        credit_card_number=data.credit_card_number,
        amount=data.amount,
        created_at=now,
    )

    payments.add(payment)
    return payment
