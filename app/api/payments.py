from datetime import datetime

from fastapi import APIRouter, Depends, status

from app.dependencies import get_now, get_payment_repository, get_user_repository
from app.repositories.payments import PaymentRepository
from app.repositories.users import UserRepository
from app.schemas.payments import PaymentCreate, PaymentOut
from app.services.payments import make_payment

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    users: UserRepository = Depends(get_user_repository),
    payments: PaymentRepository = Depends(get_payment_repository),
    now: datetime = Depends(get_now),
) -> PaymentOut:
    payment = make_payment(payload, users, payments, now)
    return PaymentOut.from_payment(payment)
