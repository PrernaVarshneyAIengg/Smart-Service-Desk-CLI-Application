
"""Presentation layer for the Smart Service Desk application.

This module handles:
- User authentication through the CLI.
- Displaying the application menu.
- Collecting user input.
- Displaying application results and errors.

Business logic and file handling are delegated to their respective layers.
"""

from getpass import getpass
from typing import Callable, Protocol

from application.auth_service import AuthService
from application.request_service import RequestService
from domain.exceptions import (
    AuthenticationError,
    InvalidInputError,
    ServiceDeskError,
)
from infrastructure.file_repository import FileRepository
from infrastructure.user_repository import FileUserRepository


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_LOGIN_ATTEMPTS = 3


# ---------------------------------------------------------------------------
# Type definitions
# ---------------------------------------------------------------------------

class AuthenticatedUser(Protocol):
    """Define the attributes required from an authenticated user."""

    username: str
    role: str


MenuAction = Callable[[RequestService, AuthenticatedUser], None]


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def login(auth_service: AuthService) -> AuthenticatedUser | None:
    """Authenticate a user with a limited number of login attempts.

    Returns:
        The authenticated user if login succeeds, otherwise None.
    """
    print("\n=== SMART SERVICE DESK LOGIN ===\n")

    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        username = input("Username: ").strip()

        try:
            password = getpass("Password: ", echo_char="*")
        except TypeError:  # Python older than 3.14 has no echo_char
            password = getpass("Password: ")

        try:
            user = auth_service.login(username, password)

            print(f"\nWelcome, {user.username} ({user.role})!")
            return user

        except AuthenticationError as error:
            print(
                f"Error: {error} "
                f"(attempt {attempt}/{MAX_LOGIN_ATTEMPTS})"
            )

    return None

def ask_login_again() -> bool:
    """Ask whether to return to the login screen or close the application.

    Returns:
        True to log in again, False to quit.
    """
    while True:
        print("\n" + "-" * 40)
        print("1. Login again")
        print("2. Quit application")
        print("-" * 40)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            return True
        if choice == "2":
            return False

        print("Error: Invalid choice. Please enter 1 or 2.")


# ---------------------------------------------------------------------------
# Presentation: Menu
# ---------------------------------------------------------------------------

def show_menu(user: AuthenticatedUser) -> None:
    """Display the main menu and the current user's session details."""
    print("\n" + "-" * 40)
    print("       SMART SERVICE DESK SYSTEM")
    print("-" * 40)
    print(f"Logged in as: {user.username} ({user.role})\n")

    print("1. Create Service Request")
    print("2. View All Requests")
    print("3. Search Request")
    print("4. Resolve Request (Admin Only)")
    print("5. Exit")

    print("-" * 40)


# ---------------------------------------------------------------------------
# Presentation: Request operations
# ---------------------------------------------------------------------------

def create_request(
    service: RequestService,
    user: AuthenticatedUser,
) -> None:
    """Collect request details and delegate creation to the service."""
    print("\n--- CREATE SERVICE REQUEST ---")

    request_id = input("Enter Request ID: ").strip()
    employee_name = input("Enter Employee Name: ").strip()
    issue = input("Enter Issue Description: ").strip()
    priority = input("Enter Priority (LOW/MEDIUM/HIGH): ").strip()

    # The application service handles validation and persistence.
    service.create_request(
        request_id,
        employee_name,
        issue,
        priority,
    )

    print("\nService Request created successfully.")


def view_requests(
    service: RequestService,
    user: AuthenticatedUser,
) -> None:
    """Retrieve and display all service requests."""
    print("\n--- ALL SERVICE REQUESTS ---")

    requests = service.view_requests()

    if not requests:
        print("No service requests found.")
        return

    for request in requests:
        print(request)


def search_request(
    service: RequestService,
    user: AuthenticatedUser,
) -> None:
    """Search for a request using its unique request ID."""
    print("\n--- SEARCH SERVICE REQUEST ---")

    request_id = input("Enter Request ID: ").strip()
    request = service.search_request(request_id)

    # Display the details of the matching request.
    print("\nRequest Details")
    print("-" * 30)
    print(f"Request ID : {request.request_id}")
    print(f"Employee   : {request.employee_name}")
    print(f"Issue      : {request.issue}")
    print(f"Priority   : {request.priority}")
    print(f"Status     : {request.status}")


def resolve_request(
    service: RequestService,
    user: AuthenticatedUser,
) -> None:
    """Request resolution through the application service.

    Authorization is enforced by the application layer, not by the CLI.
    """
    print("\n--- RESOLVE SERVICE REQUEST ---")

    request_id = input("Enter Request ID: ").strip()

    # The service verifies the user's role and request status.
    request = service.resolve_request(request_id, user)

    print(f"\nRequest {request.request_id} has been marked RESOLVED.")


# ---------------------------------------------------------------------------
# Application menu loop
# ---------------------------------------------------------------------------

def run_menu(
    service: RequestService,
    user: AuthenticatedUser,
) -> None:
    """Run the interactive menu until the user chooses to exit."""
    actions: dict[str, MenuAction] = {
        "1": create_request,
        "2": view_requests,
        "3": search_request,
        "4": resolve_request,
    }

    while True:
        show_menu(user)
        choice = input("Enter your choice: ").strip()

        # Exit without executing any further menu action.
        if choice == "5":
            print("\nGoodbye!")
            break

        try:
            action = actions.get(choice)

            # Validate the menu choice before executing an action.
            if action is None:
                raise InvalidInputError(
                    "Invalid choice. Please enter a number from 1 to 5."
                )

            action(service, user)

        except ServiceDeskError as error:
            # Display expected application errors without terminating the CLI.
            print(f"\nError: {error}")


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Initialize dependencies and start the Smart Service Desk."""
    # Composition root:
    # Instantiate concrete repositories and inject them into services.
    auth_service = AuthService(FileUserRepository())
    request_service = RequestService(FileRepository())

    while True:
        user = login(auth_service)

        if user is None:
            print("\nToo many failed attempts.")
        else:
            run_menu(request_service, user)

        # After logout or a failed login, offer to log in again or quit.
        if not ask_login_again():
            print("\nThank you for using the Smart Service Desk. Goodbye!")
            break


if __name__ == "__main__":
    main()
