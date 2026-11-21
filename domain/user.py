
"""Domain model representing an application user.

This module defines user identity, role information, and password
verification behavior for the Smart Service Desk application.
"""

import hashlib
import hmac
import secrets


# ---------------------------------------------------------------------------
# User domain model
# ---------------------------------------------------------------------------

class User:
    """Represent an authenticated application user."""

    # Supported application roles.
    ADMIN = "ADMIN"
    STAFF = "STAFF"

    # Password hashing configuration.
    _HASH_ALGORITHM = "sha256"
    _HASH_ITERATIONS = 200_000
    _SALT_LENGTH = 16

    def __init__(
        self,
        username: str,
        password_hash: str,
        role: str,
    ) -> None:
        """Initialize a user with a username, stored password hash and role.

        Args:
            username: User's login identifier.
            password_hash: Encoded password hash.
            role: User's assigned application role.
        """
        self._username = username.strip()
        self._password_hash = password_hash
        self._role = role.strip().upper()

    # -----------------------------------------------------------------------
    # Read-only properties
    # -----------------------------------------------------------------------

    @property
    def username(self) -> str:
        """Return the user's username."""
        return self._username

    @property
    def role(self) -> str:
        """Return the user's role."""
        return self._role

    # -----------------------------------------------------------------------
    # Role-based behavior
    # -----------------------------------------------------------------------

    def is_admin(self) -> bool:
        """Return whether the user has administrator privileges."""
        return self._role == self.ADMIN

    # -----------------------------------------------------------------------
    # Password verification
    # -----------------------------------------------------------------------

    def verify_password(self, password: str) -> bool:
        """Verify a password against the user's stored password hash.

        Args:
            password: Plain-text password supplied during login.

        Returns:
            True if the password matches, otherwise False.
        """
        try:
            algorithm, iterations, salt, stored_hash = (
                self._password_hash.split("$")
            )

            # Reject unsupported or malformed hash formats.
            if algorithm != "pbkdf2_sha256":
                return False

            iteration_count = int(iterations)

            candidate_hash = hashlib.pbkdf2_hmac(
                self._HASH_ALGORITHM,
                password.encode("utf-8"),
                bytes.fromhex(salt),
                iteration_count,
            ).hex()

            # Constant-time comparison helps reduce timing-based leakage.
            return hmac.compare_digest(candidate_hash, stored_hash)

        except (ValueError, TypeError):
            # Malformed stored hash or invalid input is not a match.
            return False

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Generate a salted PBKDF2 password hash.

        Args:
            password: Plain-text password to hash.

        Returns:
            Encoded hash containing algorithm, iterations, salt and digest.
        """
        salt = secrets.token_bytes(cls._SALT_LENGTH)

        password_hash = hashlib.pbkdf2_hmac(
            cls._HASH_ALGORITHM,
            password.encode("utf-8"),
            salt,
            cls._HASH_ITERATIONS,
        ).hex()

        # Store algorithm, iteration count, salt and hash together.
        return (
            f"pbkdf2_sha256$"
            f"{cls._HASH_ITERATIONS}$"
            f"{salt.hex()}$"
            f"{password_hash}"
        )
