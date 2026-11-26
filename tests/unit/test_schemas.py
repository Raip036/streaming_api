from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.payments import PaymentCreate
from app.schemas.users import UserCreate

VALID_USER = {
    "username": "sam123",
    "password": "Passw0rdX",
    "email": "sam@example.com",
    "dob": "1998-04-12",
    "creditCardNumber": "1234567812345678",
}


def user_with(**changes):
    return {**VALID_USER, **changes}


def test_valid_user_is_accepted():
    user = UserCreate.model_validate(VALID_USER)
    assert user.username == "sam123"
    assert user.dob == date(1998, 4, 12)
    assert user.credit_card_number == "1234567812345678"


def test_credit_card_is_optional():
    body = {
        key: value for key, value in VALID_USER.items() if key != "creditCardNumber"
    }  # removes credit card number section
    assert UserCreate.model_validate(body).credit_card_number is None


@pytest.mark.parametrize("email", ["not-an-email", "sam@", "@example.com", "sam example.com"])
def test_email_must_have_email_format(email):
    with pytest.raises(ValidationError):
        UserCreate.model_validate(user_with(email=email))


@pytest.mark.parametrize(
    "dob", ["12/04/1998", "1998-13-01", "1998-02-30", "yesterday", "", 893376000]
)
def test_dob_must_be_an_iso_8601_date(dob):
    with pytest.raises(ValidationError):
        UserCreate.model_validate(user_with(dob=dob))


def test_dob_in_the_future_is_rejected():
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValidationError):
        UserCreate.model_validate(user_with(dob=tomorrow))


@pytest.mark.parametrize(
    "card",
    ["123456781234567", "12345678123456789", "1234-5678-1234-5678", "abcdefghijklmnop", ""],
)
def test_credit_card_must_be_16_digits(card):
    with pytest.raises(ValidationError):
        UserCreate.model_validate(user_with(creditCardNumber=card))


def test_credit_card_keeps_leading_zeros():
    user = UserCreate.model_validate(user_with(creditCardNumber="0000567812345678"))
    assert user.credit_card_number == "0000567812345678"


@pytest.mark.parametrize("amount", [100, 999, "100"])
def test_payment_amount_of_three_digits_is_accepted(amount):
    payment = PaymentCreate.model_validate(
        {"creditCardNumber": "1234567812345678", "amount": amount}
    )
    assert payment.amount == int(amount)


@pytest.mark.parametrize("username", ["sam 123", "sam_123", "sam-123", "sam!", "", "sám", "a" * 31])
def test_username_must_be_alphanumeric_with_no_spaces(username):
    with pytest.raises(ValidationError):
        UserCreate.model_validate(user_with(username=username))


@pytest.mark.parametrize(
    "password",
    [
        "Short1A",  # 7 characters
        "nouppercase1",
        "NoNumberHere",
        "A1" + "a" * 71,  # 73 bytes, over the bcrypt limit
    ],
)
def test_password_rules(password):
    with pytest.raises(ValidationError):
        UserCreate.model_validate(user_with(password=password))


@pytest.mark.parametrize("amount", [99, 1000, 0, -100, 100.5, "abc", None])
def test_payment_amount_must_be_three_digits(amount):
    with pytest.raises(ValidationError):
        PaymentCreate.model_validate({"creditCardNumber": "1234567812345678", "amount": amount})
