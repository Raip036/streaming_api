from threading import Lock
from typing import Protocol
 
from app.models import Payment

class PaymentRepository(Protocol):
    def add(self, payment: Payment) -> None: ...

    def find_all(self) -> list[Payment]: ...

class InMemoryPaymentRepository:
    def __init__(self) -> None:
        self._payments: list[Payment] = []
        self._lock = Lock()

    def add(self, payment: Payment) -> None:
        with self._lock:
            self._payments.append(payment)

    def find_all(self) -> list[Payment]:
        with self._lock:
            return list(self._payments)
        