from app.core.security import hash_password, mask_card, verify_password


def test_hash_is_not_the_password():
    assert hash_password("Passw0rdX") != "Passw0rdX"


def test_same_password_hashes_differently():
    assert hash_password("Passw0rdX") != hash_password("Passw0rdX")


def test_correct_password_verifies():
    assert verify_password("Passw0rdX", hash_password("Passw0rdX"))


def test_wrong_password_does_not_verify():
    assert not verify_password("WrongPass1", hash_password("Passw0rdX"))


def test_mask_card_shows_only_the_last_four_digits():
    assert mask_card("1234567812345678") == "************5678"
