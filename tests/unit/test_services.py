from datetime import UTC, datetime

import pytest

from app.core.errors import CardNotRegistered, UnderAge, UsernameTaken
from app.core.security import verify_password
from app.repositories.payments import InMemoryPaymentRepository
from app.repositories.users import InMemoryUserRepository
from app.schemas.payments import PaymentCreate
from app.schemas.users import UserCreate
from app.services.payments import make_payment
from app.services.users import list_users, register_user


NOW = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)

def new_user(username="sam123", dob="1998-04-12", card="1234567812345678"):
    return UserCreate(
        username=username,
        password="Passw0rdX",
        email="sam@example.com",
        dob=dob,
        credit_card_number=card,
    )

def test_register_stores_the_user_with_a_hashed_password():
    users = InMemoryUserRepository()
    user = register_user(new_user(), users, NOW)

    assert users.exists("sam123")
    assert user.password_hash != "Passw0rdX"
    assert verify_password("Passw0rdX", user.password_hash)
    assert user.registered_at == NOW

def test_register_rejects_a_user_who_turns_18_tomorrow():
    users = InMemoryUserRepository()
    with pytest.raises(UnderAge):
        register_user(new_user(dob="2008-11-21"), users, NOW)
    assert not users.exists("sam123")

def test_register_accepts_a_user_who_turns_18_today():
    users = InMemoryUserRepository()
    register_user(new_user(dob="2008-11-20"), users, NOW)
    assert users.exists("sam123")

def test_register_rejects_a_taken_username():
    users = InMemoryUserRepository()
    register_user(new_user("sam123"), users, NOW)
    with pytest.raises(UsernameTaken):
        register_user(new_user("SAM123"), users, NOW)

def test_under_age_is_reported_before_username_taken():
    users = InMemoryUserRepository()
    register_user(new_user("sam123"), users, NOW)
    with pytest.raises(UnderAge):
        register_user(new_user("sam123", dob="2015-01-01"), users, NOW)

def test_list_users_passes_the_filter_through():
    users = InMemoryUserRepository()
    register_user(new_user("withcard"), users, NOW)
    register_user(new_user("nocard", card=None), users, NOW)

    assert len(list_users(users)) == 2
    assert [user.username for user in list_users(users, has_card=True)] == ["withcard"]
    assert [user.username for user in list_users(users, has_card=False)] == ["nocard"]

def test_payment_with_a_registered_card_is_recorded():
    users = InMemoryUserRepository()
    payments = InMemoryPaymentRepository()
    register_user(new_user(card="1234567812345678"), users, NOW)

    payment = make_payment(
        PaymentCreate(credit_card_number="1234567812345678", amount=100), users, payments, NOW
    )

    assert payment.amount == 100
    assert payments.find_all() == [payment]

def test_payment_with_an_unregistered_card_is_rejected_and_not_recorded():
    users, payments = InMemoryUserRepository(), InMemoryPaymentRepository()
    with pytest.raises(CardNotRegistered):
        make_payment(
            PaymentCreate(credit_card_number="9999999999999999", amount=100), users, payments, NOW
        )
    assert payments.find_all() == []
