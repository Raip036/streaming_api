import pytest

REGISTERED_CARD = "1234567812345678"
UNREGISTERED_CARD = "9999888877776666"


@pytest.fixture
def registered_card(client, valid_user):
    client.post("/users", json={**valid_user, "creditCardNumber": REGISTERED_CARD})
    return REGISTERED_CARD


@pytest.mark.parametrize("amount", [100, 500, 999])
def test_successful_payment_returns_201(client, registered_card, amount):
    response = client.post(
        "/payments", json={"creditCardNumber": registered_card, "amount": amount}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == amount
    assert body["creditCard"] == "************5678"
    assert body["paymentId"]
    assert "createdAt" in body


def test_each_payment_gets_its_own_id(client, registered_card):
    body = {"creditCardNumber": registered_card, "amount": 100}
    first = client.post("/payments", json=body).json()
    second = client.post("/payments", json=body).json()
    assert first["paymentId"] != second["paymentId"]


@pytest.mark.parametrize("amount", [99, 1000, 0, -100, 100.5, "abc", None])
def test_amount_that_is_not_three_digits_returns_400(client, registered_card, amount):
    response = client.post(
        "/payments", json={"creditCardNumber": registered_card, "amount": amount}
    )

    assert response.status_code == 400
    assert response.json()["error"]["details"][0]["field"] == "amount"


@pytest.mark.parametrize("card", ["123456781234567", "12345678123456789", "1234abcd1234abcd", ""])
def test_card_that_is_not_16_digits_returns_400(client, card):
    response = client.post("/payments", json={"creditCardNumber": card, "amount": 100})

    assert response.status_code == 400
    assert response.json()["error"]["details"][0]["field"] == "creditCardNumber"


@pytest.mark.parametrize("missing", ["creditCardNumber", "amount"])
def test_missing_field_returns_400(client, missing):
    body = {"creditCardNumber": REGISTERED_CARD, "amount": 100}
    del body[missing]
    assert client.post("/payments", json=body).status_code == 400


def test_invalid_body_is_reported_before_unregistered_card(client):
    response = client.post("/payments", json={"creditCardNumber": UNREGISTERED_CARD, "amount": 5})
    assert response.status_code == 400


def test_card_not_registered_to_any_user_returns_404(client, registered_card):
    response = client.post("/payments", json={"creditCardNumber": UNREGISTERED_CARD, "amount": 100})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CARD_NOT_REGISTERED"


def test_user_registered_without_a_card_cannot_be_paid_for(client, valid_user):
    del valid_user["creditCardNumber"]
    client.post("/users", json=valid_user)

    response = client.post("/payments", json={"creditCardNumber": REGISTERED_CARD, "amount": 100})
    assert response.status_code == 404


def test_payment_response_never_contains_the_full_card(client, registered_card):
    response = client.post("/payments", json={"creditCardNumber": registered_card, "amount": 100})
    assert registered_card not in response.text
