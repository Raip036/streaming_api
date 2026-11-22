import bcrypt

MAX_PASSWORD_BYTES = 72

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()) #salt is added so rainbow attacks / dictionary attacks
    return hashed.decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

def mask_card(card_number: str) -> str:
    # hides all but last 4 digits
    return "*" * (len(card_number) - 4) + card_number[-4:]


# bcrypt is deliberateltly slow, SHA-256 allows fast attacks