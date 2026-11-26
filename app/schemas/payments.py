from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.core.security import mask_card
from app.models import Payment
from app.schemas.users import CARD_PATTERN


class PaymentCreate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    credit_card_number: str = Field(pattern=CARD_PATTERN)
    amount: int = Field(ge=100, le=999)


class PaymentOut(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    payment_id: str
    credit_card: str
    amount: int
    created_at: datetime

    @classmethod
    def from_payment(cls, payment: Payment) -> "PaymentOut":
        return cls(
            payment_id=payment.id,
            credit_card=mask_card(payment.credit_card_number),
            amount=payment.amount,
            created_at=payment.created_at,
        )
