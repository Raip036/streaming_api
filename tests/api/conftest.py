import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_payment_repository, get_user_repository
from app.main import app
from app.repositories.payments import InMemoryPaymentRepository
from app.repositories.users import InMemoryUserRepository


@pytest.fixture
def client():
    # A client whose app starts every test with empty storage.
    users = InMemoryUserRepository()
    payments = InMemoryPaymentRepository()
    app.dependency_overrides[get_user_repository] = lambda: users
    app.dependency_overrides[get_payment_repository] = lambda: payments
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def valid_user():
    return {
        "username": "sam123",
        "password": "Passw0rdX",
        "email": "sam@example.com",
        "dob": "1998-04-12",
        "creditCardNumber": "1234567812345678",
    }
