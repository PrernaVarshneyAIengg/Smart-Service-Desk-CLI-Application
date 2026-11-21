
"""Application service responsible for service request operations."""

from domain.exceptions import (
    DuplicateRequestError,
    PermissionDeniedError,
    RequestNotFoundError,
)
from domain.repository import RequestRepository
from domain.service_request import ServiceRequest
from domain.user import User


class RequestService:
    """Handles service request operations and business rules."""

    def __init__(self, repository: RequestRepository) -> None:
        """
        Initialize the service with a request repository.

        The service depends on an abstract repository,
        not a specific file storage implementation.
        """
        self._repository = repository

    def create_request(
        self,
        request_id: str,
        employee_name: str,
        issue: str,
        priority: str,
    ) -> ServiceRequest:
        """Create and persist a new service request."""
        request = ServiceRequest(
            request_id,
            employee_name,
            issue,
            priority,
        )

        if self._repository.get_by_id(request.request_id) is not None:
            raise DuplicateRequestError(
                f"Request ID {request.request_id} already exists."
            )

        self._repository.save(request)
        return request

    def view_requests(self) -> list[ServiceRequest]:
        """Return all stored service requests."""
        return self._repository.get_all()

    def search_request(self, request_id: str) -> ServiceRequest:
        """Retrieve a request by ID or raise an exception."""
        request = self._repository.get_by_id(request_id)

        if request is None:
            normalized_id = request_id.strip().upper()
            raise RequestNotFoundError(
                f"Request not found: {normalized_id}"
            )

        return request

    def resolve_request(
        self,
        request_id: str,
        user: User,
    ) -> ServiceRequest:
        """Resolve a request if the user has admin privileges."""
        if not user.is_admin():
            raise PermissionDeniedError(
                "Only an admin can resolve requests."
            )

        request = self.search_request(request_id)
        request.resolve()

        self._repository.save(request)
        return request
