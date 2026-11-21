
"""Custom exception definitions for the Smart Service Desk application.

This module provides a common exception hierarchy for handling expected
business and application errors in a consistent manner.
"""


# ---------------------------------------------------------------------------
# Base application exception
# ---------------------------------------------------------------------------

class ServiceDeskError(Exception):
    """Base class for expected Smart Service Desk application errors."""


# ---------------------------------------------------------------------------
# Service request exceptions
# ---------------------------------------------------------------------------

class DuplicateRequestError(ServiceDeskError):
    """Raised when a request ID already exists in the system."""


class RequestNotFoundError(ServiceDeskError):
    """Raised when a requested service ticket cannot be found."""


class InvalidPriorityError(ServiceDeskError):
    """Raised when a service request contains an invalid priority."""


class InvalidInputError(ServiceDeskError):
    """Raised when user input or request data is invalid."""


class RequestAlreadyResolvedError(ServiceDeskError):
    """Raised when an attempt is made to resolve an already resolved request."""


# ---------------------------------------------------------------------------
# Authentication and authorization exceptions
# ---------------------------------------------------------------------------

class AuthenticationError(ServiceDeskError):
    """Raised when user authentication fails."""


class PermissionDeniedError(ServiceDeskError):
    """Raised when a user attempts an operation without sufficient permission."""
