# Streaming API

My solution to the Reply technical task: a small API for a video streaming service where
users can register and make a payment with a registered credit card.

It's written in Python with FastAPI. Data is kept in memory, as the brief allows, so it
resets whenever the server restarts.

## Running it

You need Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

The API is then at http://127.0.0.1:8000. The easiest way to try it is the interactive
docs page at http://127.0.0.1:8000/docs.

To run the tests:

```bash
pytest
```

## Endpoints

### POST /users

Registers a user.

```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"sam123","password":"Passw0rdX","email":"sam@example.com","dob":"1998-04-12","creditCardNumber":"1234567812345678"}'
```

| Field | Rule |
| --- | --- |
| `username` | Letters and numbers only, no spaces |
| `password` | At least 8 characters, with at least one upper case letter and one number |
| `email` | Must be a valid email address |
| `dob` | ISO 8601 date, e.g. `1998-04-12` |
| `creditCardNumber` | Optional. 16 digits if given |

| Response | When |
| --- | --- |
| 201 | User registered |
| 400 | The request body fails validation |
| 403 | The user is under 18 |
| 409 | The username is already taken |

The password is never returned, and only the last four digits of the card are shown.

### GET /users

Lists registered users. An optional `CreditCard` filter narrows the list.

```bash
curl "http://127.0.0.1:8000/users"
curl "http://127.0.0.1:8000/users?CreditCard=Yes"
curl "http://127.0.0.1:8000/users?CreditCard=No"
```

`Yes` returns users with a card, `No` returns users without one, and leaving it out
returns everyone. Any other value gets a 400.

### POST /payments

Takes a payment against a registered card.

```bash
curl -i -X POST http://127.0.0.1:8000/payments \
  -H "Content-Type: application/json" \
  -d '{"creditCardNumber":"1234567812345678","amount":100}'
```

| Field | Rule |
| --- | --- |
| `creditCardNumber` | 16 digits |
| `amount` | 3 digits, so a whole number from 100 to 999 |

| Response | When |
| --- | --- |
| 201 | Payment recorded |
| 400 | The request body fails validation |
| 404 | The card isn't registered to any user |

### Errors

Every error comes back in the same shape:

```json
{
  "error": {
    "code": "UNDER_AGE",
    "message": "Users must be at least 18 years old",
    "details": []
  }
}
```

There is also a `GET /health` endpoint that returns `{"status": "ok"}`.

## Assumptions

The brief left a few things open, so these are the calls I made:

- Usernames are not case sensitive when checking for duplicates. `Sam` and `sam` count as
  the same user.
- Usernames can be up to 30 characters and passwords up to 72 bytes. 72 is the most that
  bcrypt will actually use.
- Date of birth is a plain date (`YYYY-MM-DD`). A date in the future is treated as invalid
  input (400), not as an under-age user (403).
- Someone who turns 18 today is allowed to register.
- Card numbers are stored as text so leading zeros aren't lost. I only check for 16 digits,
  because that's all the brief asks for.
- Two users can register the same card.
- "Amount: 3 digits" is read as a whole number between 100 and 999.
- If a request breaks more than one rule, the checks run in the order the brief lists
  them: 400, then 403, then 409.
- The `CreditCard` filter accepts `Yes` and `No` in any letter case.
- The free trial and subscription types are mentioned in the brief but nothing is required
  of them, so I haven't built them. I do store when each user registered.

## How it's put together

```
app/
  api/           routes: read the request, call a service, return the response
  schemas/       the shape of the JSON going in and out, and the validation rules
  services/      the business rules (age check, duplicate usernames, registered cards)
  repositories/  in-memory storage for users and payments
  core/          error handling, the age calculation, password hashing, card masking
tests/
  unit/          tests that call the code directly
  api/           tests that send requests through the whole app
```

A few things worth pointing out:

- The services don't know anything about HTTP. They raise errors like `UnderAge`, and
  one handler turns those into status codes. That keeps the rules easy to test.
- Storage sits behind a small interface, so swapping the in-memory version for a real
  database wouldn't touch the rest of the code.
- Checking a username and saving the user happen under a lock, so two people registering
  the same name at the same moment can't both succeed.
- Passwords are hashed with bcrypt and never stored or returned in plain text.

## Tests

There are 132 tests covering 98% of the code. The API tests are named after the rules in
the brief, so the test list reads roughly like the spec.

```bash
pytest --cov=app
```

## What I'd change for real production use

- Not store card numbers at all. A payment provider should hold the card and hand back a
  token. I only store them here because the task needs payments matched to registered cards.
- Use a real database, since everything is lost on restart.
- Add authentication. Right now anyone can list every user.
- Make payments safe to retry, so a client that sends the same payment twice isn't charged
  twice.
- Add pagination to the user list, and rate limiting.
