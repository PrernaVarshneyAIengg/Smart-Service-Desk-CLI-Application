
"""JSON-based persistence implementation for service requests.

This module implements the RequestRepository abstraction and handles
reading, writing, searching, and updating service requests in a JSON file.
"""

import json
import os
import tempfile
from pathlib import Path

from domain.repository import RequestRepository
from domain.service_request import ServiceRequest


# ---------------------------------------------------------------------------
# File path configuration
# ---------------------------------------------------------------------------

# Resolve the project root relative to this module, rather than the current
# working directory. This ensures the data file is located consistently.
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PATH = BASE_DIR / "data" / "requests.json"


# ---------------------------------------------------------------------------
# JSON repository implementation
# ---------------------------------------------------------------------------

class FileRepository(RequestRepository):
    """Persist service requests using a JSON file.

    This class implements the RequestRepository contract and provides
    concrete persistence operations using local JSON storage.
    """

    def __init__(self, file_path: Path | str = DEFAULT_PATH) -> None:
        """Initialize the repository with the configured storage path.

        Args:
            file_path: Path to the JSON file used for storing requests.
        """
        self._file_path = Path(file_path)

    # -----------------------------------------------------------------------
    # Public repository methods
    # -----------------------------------------------------------------------

    def get_all(self) -> list[ServiceRequest]:
        """Retrieve all persisted service requests."""
        return self._load()

    def get_by_id(self, request_id: str) -> ServiceRequest | None:
        """Retrieve a request by its ID.

        Args:
            request_id: Unique identifier of the requested service ticket.

        Returns:
            The matching ServiceRequest, or None if no match exists.
        """
        normalized_id = request_id.strip().upper()

        for request in self._load():
            if request.request_id == normalized_id:
                return request

        return None

    def save(self, request: ServiceRequest) -> None:
        """Insert a new request or update an existing request.

        The request is matched using its unique request ID. If a matching
        record exists, it is replaced; otherwise, it is appended.

        Args:
            request: ServiceRequest object to persist.
        """
        requests = self._load()

        for index, existing_request in enumerate(requests):
            if existing_request.request_id == request.request_id:
                requests[index] = request
                break
        else:
            # Append the request if no existing ID was found.
            requests.append(request)

        self._write(requests)

    # -----------------------------------------------------------------------
    # Private file-handling methods
    # -----------------------------------------------------------------------

    def _load(self) -> list[ServiceRequest]:
        """Load and deserialize service requests from the JSON file.

        Returns:
            A list of ServiceRequest objects.

        Raises:
            ValueError: If the JSON file contains malformed or invalid data.
        """
        if not self._file_path.exists():
            return []

        try:
            content = self._file_path.read_text(encoding="utf-8").strip()

            # Treat an empty file as an empty collection.
            if not content:
                return []

            raw_items = json.loads(content)

        except json.JSONDecodeError as error:
            # Avoid silently treating corrupted data as an empty collection.
            raise ValueError(
                f"Invalid JSON data in '{self._file_path}'."
            ) from error

        # Ensure the JSON root contains a list of request records.
        if not isinstance(raw_items, list):
            raise ValueError(
                f"Expected a JSON list in '{self._file_path}'."
            )

        try:
            return [
                ServiceRequest.from_dict(item)
                for item in raw_items
            ]

        except (TypeError, KeyError, ValueError) as error:
            raise ValueError(
                f"Invalid service request data in '{self._file_path}'."
            ) from error

    def _write(self, requests: list[ServiceRequest]) -> None:
        """Serialize and persist requests using an atomic file replacement.

        A temporary file is written first and then replaced with the
        destination file. This helps prevent partially written JSON data.

        Args:
            requests: Collection of ServiceRequest objects to persist.
        """
        # Create the parent directory if it does not already exist.
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        serialized_data = [
            request.to_dict()
            for request in requests
        ]

        # Write to a temporary file in the same directory to support atomic
        # replacement on the same filesystem.
        temp_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._file_path.parent,
                delete=False,
            ) as temp_file:
                json.dump(
                    serialized_data,
                    temp_file,
                    indent=4,
                    ensure_ascii=False,
                )
                temp_file.write("\n")
                temp_path = Path(temp_file.name)

            # Replace the original file only after the temporary file is
            # successfully written.
            os.replace(temp_path, self._file_path)

        finally:
            # Remove any temporary file left behind after a failed write.
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()
