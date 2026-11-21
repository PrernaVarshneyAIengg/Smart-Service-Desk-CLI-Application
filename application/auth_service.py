
"""Application service responsible for user authentication."""

from domain.exceptions import AuthenticationError
from domain.repository import UserRepository
from domain.user import User


class AuthService:
    """Authenticates users using the user repository."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize the service with a user repository."""
        self._user_repository = user_repository

    def login(self, username: str, password: str) -> User:
        """
        Authenticate a user using their username and password.

        Raises:
            AuthenticationError: If the credentials are invalid.
        """
        user = self._user_repository.get_by_username(username)

        if user is None or not user.verify_password(password):
            raise AuthenticationError("Invalid username or password.")

        return user
