
"""Abstract repository contracts for the Smart Service Desk domain.

These interfaces define the persistence operations required by the
application. Concrete implementations belong to the infrastructure layer.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imports used only for static type checking.
    # This avoids unnecessary runtime import dependencies.
    from domain.service_request import ServiceRequest
    from domain.user import User


# ---------------------------------------------------------------------------
# Service request repository contract
# ---------------------------------------------------------------------------

class RequestRepository(ABC):
    """Define the contract for service request persistence.

    The domain/application layers specify WHAT operations are required.
    Infrastructure implementations determine HOW data is stored.
    """

    @abstractmethod
    def get_all(self) -> list["ServiceRequest"]:
        """Return all persisted service requests."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, request_id: str) -> "ServiceRequest | None":
        """Retrieve a request by ID, or return None if it does not exist."""
        raise NotImplementedError

    @abstractmethod
    def save(self, request: "ServiceRequest") -> None:
        """Insert a new request or update an existing request."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# User repository contract
# ---------------------------------------------------------------------------

class UserRepository(ABC):
    """Define the contract for user account retrieval."""

    @abstractmethod
    def get_by_username(self, username: str) -> "User | None":
        """Retrieve a user by username, or return None if not found."""
        raise NotImplementedError
