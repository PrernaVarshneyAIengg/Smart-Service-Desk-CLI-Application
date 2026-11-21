
"""Domain model representing an IT service desk request.

This module defines the ServiceRequest entity, its validation rules,
and its business behavior independently of storage or presentation.
"""

from domain.exceptions import (
    InvalidInputError,
    InvalidPriorityError,
    RequestAlreadyResolvedError,
)


# ---------------------------------------------------------------------------
# Service request domain model
# ---------------------------------------------------------------------------

class ServiceRequest:
    """Represent an individual IT support request.

    A service request contains employee details, issue information,
    priority, and its current lifecycle status.
    """

    # Supported priority levels.
    VALID_PRIORITIES = ("LOW", "MEDIUM", "HIGH")

    # Supported lifecycle statuses.
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"

    def __init__(
        self,
        request_id: str,
        employee_name: str,
        issue: str,
        priority: str,
        status: str = OPEN,
    ) -> None:
        """Initialize and validate a service request.

        Args:
            request_id: Unique identifier for the request.
            employee_name: Name of the employee raising the issue.
            issue: Description of the reported problem.
            priority: Priority level of the request.
            status: Current lifecycle status, defaulting to OPEN.
        """
        # Validate and normalize all input before assigning attributes.
        self._request_id = self._require_text(
            request_id, "Request ID"
        ).upper()

        self._employee_name = self._require_text(
            employee_name, "Employee name"
        )

        self._issue = self._require_text(
            issue, "Issue description"
        )

        self._priority = self._validate_priority(priority)
        self._status = self._validate_status(status)

    # -----------------------------------------------------------------------
    # Read-only properties
    # -----------------------------------------------------------------------

    @property
    def request_id(self) -> str:
        """Return the unique request identifier."""
        return self._request_id

    @property
    def employee_name(self) -> str:
        """Return the name of the employee associated with the request."""
        return self._employee_name

    @property
    def issue(self) -> str:
        """Return the issue description."""
        return self._issue

    @property
    def priority(self) -> str:
        """Return the request priority."""
        return self._priority

    @property
    def status(self) -> str:
        """Return the current request status."""
        return self._status

    # -----------------------------------------------------------------------
    # Business behavior
    # -----------------------------------------------------------------------

    def resolve(self) -> None:
        """Transition an open request to RESOLVED.

        Raises:
            RequestAlreadyResolvedError: If the request is already resolved.
        """
        # Prevent repeated resolution of the same request.
        if self._status == self.RESOLVED:
            raise RequestAlreadyResolvedError(
                f"Request {self._request_id} is already RESOLVED."
            )

        # Update the status only when the request is currently OPEN.
        self._status = self.RESOLVED

    # -----------------------------------------------------------------------
    # Serialization and deserialization
    # -----------------------------------------------------------------------

    def to_dict(self) -> dict[str, str]:
        """Convert the domain object into a dictionary.

        This representation can be used by repositories for persistence.
        """
        return {
            "request_id": self._request_id,
            "employee_name": self._employee_name,
            "issue": self._issue,
            "priority": self._priority,
            "status": self._status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "ServiceRequest":
        """Reconstruct a domain object from a dictionary.

        Args:
            data: Dictionary containing serialized request information.

        Returns:
            A validated ServiceRequest instance.
        """
        return cls(
            request_id=data["request_id"],
            employee_name=data["employee_name"],
            issue=data["issue"],
            priority=data["priority"],
            status=data["status"],
        )

    # -----------------------------------------------------------------------
    # Object representation
    # -----------------------------------------------------------------------

    def __str__(self) -> str:
        """Return a readable representation for CLI display."""
        return (
            f"{self._request_id} | "
            f"{self._employee_name} | "
            f"{self._issue} | "
            f"{self._priority} | "
            f"{self._status}"
        )

    # -----------------------------------------------------------------------
    # Validation helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        """Validate that a required field contains non-whitespace text.

        Args:
            value: Input value to validate.
            field_name: Name of the field for the error message.

        Returns:
            The trimmed string value.

        Raises:
            InvalidInputError: If the field is empty or invalid.
        """
        if not isinstance(value, str) or not value.strip():
            raise InvalidInputError(
                f"{field_name} cannot be empty."
            )

        return value.strip()

    @classmethod
    def _validate_priority(cls, priority: str) -> str:
        """Validate and normalize the request priority.

        Args:
            priority: Priority value supplied by the caller.

        Returns:
            The normalized priority.

        Raises:
            InvalidPriorityError: If the priority is unsupported.
        """
        if not isinstance(priority, str):
            raise InvalidPriorityError(
                "Priority must be LOW, MEDIUM or HIGH."
            )

        normalized_priority = priority.strip().upper()

        if normalized_priority not in cls.VALID_PRIORITIES:
            raise InvalidPriorityError(
                "Priority must be LOW, MEDIUM or HIGH."
            )

        return normalized_priority

    @classmethod
    def _validate_status(cls, status: str) -> str:
        """Validate and normalize the request status.

        Args:
            status: Status value supplied by the caller.

        Returns:
            The normalized status.

        Raises:
            InvalidInputError: If the status is unsupported.
        """
        if not isinstance(status, str):
            raise InvalidInputError(
                "Status must be OPEN or RESOLVED."
            )

        normalized_status = status.strip().upper()

        if normalized_status not in (cls.OPEN, cls.RESOLVED):
            raise InvalidInputError(
                "Status must be OPEN or RESOLVED."
            )

        return normalized_status
