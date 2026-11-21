
"""JSON-based persistence implementation for application users.

This module implements the UserRepository abstraction and handles
loading, retrieving, and initializing user records using JSON storage.
"""

import json
import os
import tempfile
from pathlib import Path

from domain.repository import UserRepository
from domain.user import User


# ---------------------------------------------------------------------------
# File path configuration
# ---------------------------------------------------------------------------

# Resolve the project root independently of the current working directory.
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PATH = BASE_DIR / "data" / "users.json"


# ---------------------------------------------------------------------------
# User repository implementation
# ---------------------------------------------------------------------------

class FileUserRepository(UserRepository):
    """Persist and retrieve user records using a JSON file."""

    def __init__(self, file_path: Path | str = DEFAULT_PATH) -> None:
        """Initialize the repository and ensure default users exist.

        Args:
            file_path: Path to the JSON file containing user records.
        """
        self._file_path = Path(file_path)

        # Seed default accounts only when the storage file is missing or empty.
        self._ensure_default_users()

    # -----------------------------------------------------------------------
    # Public repository methods
    # -----------------------------------------------------------------------

    def get_by_username(self, username: str) -> User | None:
        """Retrieve a user by username, ignoring case differences.

        Args:
            username: Username used to identify the account.

        Returns:
            A User object if the account exists, otherwise None.
        """
        normalized_username = username.strip().lower()

        for item in self._load():
            if item["username"].strip().lower() == normalized_username:
                return User(
                    item["username"],
                    item["password_hash"],
                    item["role"],
                )

        return None

    # -----------------------------------------------------------------------
    # Private file-handling methods
    # -----------------------------------------------------------------------

    def _load(self) -> list[dict[str, str]]:
        """Load user records from the JSON file.

        Returns:
            A list of dictionaries containing user data.

        Raises:
            ValueError: If the JSON file contains malformed or invalid data.
        """
        if not self._file_path.exists():
            return []

        try:
            content = self._file_path.read_text(encoding="utf-8").strip()

            # Treat an empty file as an empty user collection.
            if not content:
                return []

            raw_users = json.loads(content)

        except json.JSONDecodeError as error:
            # Avoid treating corrupted user data as an empty collection.
            raise ValueError(
                f"Invalid JSON data in '{self._file_path}'."
            ) from error

        # Validate the root structure before processing individual records.
        if not isinstance(raw_users, list):
            raise ValueError(
                f"Expected a JSON list in '{self._file_path}'."
            )

        # Validate each record to ensure it contains the expected fields.
        required_fields = {"username", "password_hash", "role"}

        for index, item in enumerate(raw_users):
            if not isinstance(item, dict) or not required_fields.issubset(item):
                raise ValueError(
                    f"Invalid user record at index {index} "
                    f"in '{self._file_path}'."
                )

            if not all(
                isinstance(item[field], str)
                for field in required_fields
            ):
                raise ValueError(
                    f"User record at index {index} contains invalid field types."
                )

        return raw_users

    def _ensure_default_users(self) -> None:
        """Create demo accounts if the storage file is missing or empty.

        Existing user records are preserved. Default accounts are not
        recreated if the JSON file contains existing user data.
        """
        if self._load():
            return

        default_users = [
            {
                "username": "admin",
                "password_hash": User.hash_password("admin123"),
                "role": User.ADMIN,
            },
            {
                "username": "staff",
                "password_hash": User.hash_password("staff123"),
                "role": User.STAFF,
            },
        ]

        self._write(default_users)

    def _write(self, users: list[dict[str, str]]) -> None:
        """Persist user records using an atomic file replacement.

        Args:
            users: Collection of user records to write.
        """
        # Create the parent directory if it does not already exist.
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path: Path | None = None

        try:
            # Write the data to a temporary file before replacing the original.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._file_path.parent,
                delete=False,
            ) as temp_file:
                json.dump(
                    users,
                    temp_file,
                    indent=4,
                    ensure_ascii=False,
                )
                temp_file.write("\n")
                temp_path = Path(temp_file.name)

            # Replace the destination only after writing succeeds.
            os.replace(temp_path, self._file_path)

        finally:
            # Clean up the temporary file if replacement was unsuccessful.
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()
