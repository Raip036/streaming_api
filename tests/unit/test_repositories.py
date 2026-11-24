from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime

from app.models import Payment, User
from app.repositories.payments import InMemoryPaymentRepository
from app.repositories.users import InMemoryUserRepository

def make_user(username="sam123", card="1234567812345678"):
    return User(
        username=username,
        password_hash="hashed",
        email=f"{username}@example.com",
        dob=date(1998, 4, 12),
        credit_card_number=card,
        registered_at=datetime(2026, 11, 20, tzinfo=UTC),
    )

def test_added_user_exists():
    repo = InMemoryUserRepository()
    assert repo.add(make_user("sam123"))
    assert repo.exists("sam123")

def test_usernames_are_compared_without_regard_to_case():
    repo = InMemoryUserRepository()
    repo.add(make_user("Sam123"))
    assert repo.exists("sam123")
    assert not repo.add(make_user("SAM123"))

def test_adding_a_taken_username_returns_false_and_keeps_the_original():
    repo = InMemoryUserRepository()
    repo.add(make_user("sam123", card="1111222233334444"))
    assert not repo.add(make_user('sam123', card="5555666677778888"))
    assert repo.find_all()[0].credit_card_number == "1111222233334444"

def test_find_all_filters_by_card():
    repo = InMemoryUserRepository()
    repo.add(make_user("withcard"))
    repo.add(make_user("nocard", card=None))

    assert len(repo.find_all()) == 2
    assert [user.username for user in repo.find_all(has_card=True)] == ["withcard"]
    assert [user.username for user in repo.find_all(has_card=False)] == ["nocard"]

def test_card_exists_only_for_registered_cards():
    repo = InMemoryUserRepository()
    repo.add(make_user("sam123", card="1234567812345678"))
    assert repo.card_exists("1234567812345678")
    assert not repo.card_exists("9999999999999999")

def test_only_one_of_many_simultaneous_registrations_wins():
    repo = InMemoryUserRepository()
    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(lambda _: repo.add(make_user("sam123")), range(200)))

    assert results.count(True) == 1
    assert len(repo.find_all()) == 1

def test_payment_repository_stores_payments():
    repo = InMemoryPaymentRepository()
    payment = Payment
    payment = Payment("id-1", "1234567812345678", 100, datetime(2026, 11, 20, tzinfo=UTC))
    repo.add(payment)
    assert repo.find_all() == [payment]