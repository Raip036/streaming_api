from datetime import date

import pytest

def years_ago(years: int, days_offset: int = 0) -> str:
    """An ISO date that many years before today, shifted by some days."""
    today = date.today()
    try:
        shifted = today.replace(year=today.year - years)
    except ValueError:  # today is 29 February and the target year has no such day
        shifted = today.replace(year=today.year - years, day=28)
    return date.fromordinal(shifted.toordinal() + days_offset).isoformat()

def test_successful_registration_returns_201(client, valid_user):
    response = client.post("/users", json=valid_user)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "sam123"
    assert body["email"] == "sam@example.com"
    assert body["dob"] == "1998-04-12"
    assert body["creditCard"] == "************5678"
    assert "registeredAt" in body

@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("username", "sam 123"),
        ("username", "sam_123"),
        ("username", ""),
        ("password", "Short1A"),
        ("password", "nouppercase1"),
        ("password", "NoNumberHere"),
        ("email", "not-an-email"),
        ("dob", "12/04/1998"),
        ("dob", "1998-02-30"),
        ("creditCardNumber", "123456781234567"),
        ("creditCardNumber", "12345678123456789"),
        ("creditCardNumber", "1234abcd1234abcd"),
    ],
)
def test_invalid_field_returns_400(client, valid_user, field, bad_value):
    valid_user[field] = bad_value
    response = client.post("/users", json=valid_user)

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["field"] == field

def test_malformed_json_returns_400(client):
    response = client.post(
        "/users", content="{not json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

def test_user_under_18_returns_403(client, valid_user):
    valid_user["dob"] = years_ago(17)
    response = client.post("/users", json=valid_user)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "UNDER_AGE"

def test_user_who_turns_18_tomorrow_returns_403(client, valid_user):
    valid_user["dob"] = years_ago(18, days_offset=1)
    assert client.post("/users", json=valid_user).status_code == 403

def test_user_who_turns_18_today_returns_201(client, valid_user):
    valid_user["dob"] = years_ago(18)
    assert client.post("/users", json=valid_user).status_code == 201

def test_username_already_used_returns_409(client, valid_user):
    assert client.post("/users", json=valid_user).status_code == 201
    response = client.post("/users", json=valid_user)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "USERNAME_TAKEN"

def test_invalid_and_under_age_returns_400(client, valid_user):
    valid_user["dob"] = years_ago(10)
    valid_user["password"] = "weak"
    assert client.post("/users", json=valid_user).status_code == 400

def test_under_age_and_duplicate_username_returns_403(client, valid_user):
    client.post("/users", json=valid_user)
    valid_user["dob"] = years_ago(10)
    assert client.post("/users", json=valid_user).status_code == 403


@pytest.fixture
def three_users(client, valid_user):
    client.post("/users", json={**valid_user, "username": "card1"})
    client.post(
        "/users",
        json={**valid_user, "username": "card2", "creditCardNumber": "1111222233334444"},
    )
    no_card = {k: v for k, v in valid_user.items() if k != "creditCardNumber"}
    client.post("/users", json={**no_card, "username": "nocard"})


def usernames(response):
    return sorted(user["username"] for user in response.json())

def test_credit_card_yes_returns_users_with_a_card(client, three_users):
    response = client.get("/users", params={"CreditCard": "Yes"})
    assert response.status_code == 200
    assert usernames(response) == ["card1", "card2"]

@pytest.mark.parametrize("value", ["Maybe", "true", "1", ""])
def test_invalid_filter_value_returns_400(client, value):
    response = client.get("/users", params={"CreditCard": value})
    assert response.status_code == 400
    assert response.json()["error"]["details"][0]["field"] == "CreditCard"

def test_responses_never_contain_the_password_or_the_full_card(client, valid_user):
    created = client.post("/users", json=valid_user)
    listed = client.get("/users")

    for response in (created, listed):
        assert "Passw0rdX" not in response.text
        assert "password" not in response.text.lower()
        assert "1234567812345678" not in response.text


def test_validation_errors_do_not_echo_the_rejected_value(client, valid_user):
    valid_user["password"] = "secretbutweak"
    valid_user["creditCardNumber"] = "12345678"
    response = client.post("/users", json=valid_user)

    assert response.status_code == 400
    assert "secretbutweak" not in response.text
    assert "12345678" not in response.text