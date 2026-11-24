from threading import Lock
from typing import Protocol

from app.models import User 

class UserRepository(Protocol):

    def add(self, user: User) -> bool: ...

    def exists(self, username: str) -> bool: ...

    def find_all(self, has_card: bool | None = None) -> list[User]: ...

    def card_exists(self, card_number: str) -> bool: ...


class InMemoryUserRepository:

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._lock - Lock()

    @staticmethod
    def _key(username: str) -> str:
        return username.lower()

    def add(self, user: User) -> bool:
        key = self._key(user.username)
        with self._lock:
            if key in self._users:
                return False
            self._users[key] = user
            return True

    def exists(self, username: str) -> bool:
        with self._lock:
            return self._key(username in self._users)

    def find_all(self, has_card: bool | None = None) -> list[User]:
        with self._lock:
            users = list(self._users.values())
        if has_card is None:
            return users
        return [user for user in users if (user.credit_card_number is not None) == has_card] #list comprehension for users with card

    def card_exists(self, card_number: str) -> bool:
        with self._lock:
            return any(user.credit_card_number == card_number for user in self._users.values())
        
        




