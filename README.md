# Smart Service Desk Management System

A command-line based IT Service Desk Management System built using Python and Object-Oriented Programming. It enables authenticated users to create, view, and search IT service requests, while administrators can resolve requests through role-based access control.

## Problem Statement

IT support requests are often tracked manually, making it difficult to organize, monitor, and manage issues efficiently. This application provides a structured solution by managing service requests through a command-line interface, storing records persistently in JSON files, and enforcing role-based permissions.

## Features

- **User Authentication:** Login system with ADMIN and STAFF roles, with a maximum of three login attempts. After logging out or failing all attempts, the user can choose to log in again or quit the application.
- **Create Requests:** Create IT service requests with employee details, issue descriptions, and priority levels.
- **Duplicate Prevention:** Rejects service requests with duplicate IDs.
- **View Requests:** Display all stored service requests.
- **Search Requests:** Retrieve a request using its Request ID.
- **Request Resolution:** Only administrators can resolve open requests.
- **Request Lifecycle:** Requests follow an OPEN to RESOLVED status transition.
- **Persistent Storage:** Requests and user records are stored in JSON files.
- **Input Validation:** Validates request details, priorities, and user input.
- **Exception Handling:** Handles invalid inputs, duplicate IDs, missing requests, authentication failures, and unauthorized actions.
- **Secure Password Hashing:** Uses salted PBKDF2 password hashing instead of storing plaintext passwords.

## Getting Started

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <YOUR_REPOSITORY_URL>
```

Navigate to the project directory:

```bash
cd smart-service-desk
```

Replace `<YOUR_REPOSITORY_URL>` with the HTTPS or SSH URL of your GitHub repository.

### 2. Create a Virtual Environment

Create the environment inside the project folder:

```bash
# Linux / macOS
python3 -m venv .venv

# Windows
python -m venv .venv
```

### 3. Activate the Virtual Environment

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

The terminal prompt should now start with `(.venv)`.

### 4. Run the Application

```bash
python main.py
```

No `pip install` step is needed because the project uses only the Python standard library.

To leave the virtual environment when you are finished:

```bash
deactivate
```

> The `.venv/` folder is listed in `.gitignore`, so it is not committed to the repository.

## Default Users

| Username | Password | Role |
|----------|----------|----------|
| admin | admin123 | ADMIN |
| staff | staff123 | STAFF |

Demo accounts are automatically initialized in `data/users.json` if no user records exist.

Passwords are stored as salted PBKDF2 hashes.

> These credentials are intended for demonstration purposes only.

## Technologies Used

- Python
- JSON
- Git & GitHub

## Concepts Used

- **Object-Oriented Programming (OOP):** Uses classes, constructors, encapsulation, properties, and methods to model users and service requests.
- **Abstraction:** Abstract repository classes define contracts for data access, implemented by infrastructure classes.
- **SOLID Principles:** Applies Single Responsibility Principle and Dependency Inversion Principle to maintain separation of responsibilities and reduce coupling.
- **Exception Handling:** Custom exceptions derived from `ServiceDeskError` handle application-specific errors.
- **File Handling:** JSON-based persistence for storing and retrieving requests and user records.
- **Layered Architecture:** Separates domain, application, infrastructure, and presentation responsibilities.
- **Dependency Injection:** Repository implementations are injected into application services.
- **Data Validation:** Validates user inputs, request IDs, priorities, and request status.
- **Password Security:** Uses PBKDF2 with a random salt for password hashing and verification.
- **Version Control:** Uses Git branches, commits, and merge workflows for development.

## Project Structure

```text
smart-service-desk/
│
├── domain/
│   ├── service_request.py    # Service request entity and business rules
│   ├── user.py               # User entity, roles and password verification
│   ├── repository.py          # Abstract repository contracts
│   └── exceptions.py          # Custom application exceptions
│
├── application/
│   ├── request_service.py    # Request creation, search, view and resolution
│   └── auth_service.py       # User authentication
│
├── infrastructure/
│   ├── file_repository.py   # JSON request storage implementation
│   └── user_repository.py   # JSON user storage implementation
│
├── data/
│   ├── requests.json        # Persistent service request records
│   └── users.json           # User records and password hashes
│
├── main.py                  # CLI, menu and application entry point
├── README.md
└── .gitignore
```

## How the Application Works

1. `main.py` initializes the repository implementations and injects them into the application services.
2. The user logs in through the CLI, and `AuthService` validates credentials using `UserRepository`.
3. After authentication, the application displays the menu according to the user's role.
4. `RequestService` handles request creation, viewing, searching, and resolution.
5. `ServiceRequest` validates request data and manages request status transitions.
6. Repository abstractions separate business logic from file storage.
7. `FileRepository` manages request data in `data/requests.json`.
8. `FileUserRepository` manages user records in `data/users.json`.
9. Only administrators can resolve requests, enforced by `RequestService`, while `ServiceRequest.resolve()` ensures the request lifecycle rules are followed.
10. When the user exits the menu or fails all login attempts, the application asks whether to log in again or quit.

## Architecture

The project follows a layered architecture:

- **Presentation Layer:** `main.py` handles menus, user input, and output.
- **Application Layer:** `AuthService` and `RequestService` orchestrate application operations.
- **Domain Layer:** `User`, `ServiceRequest`, repository abstractions, and custom exceptions define the core logic.
- **Infrastructure Layer:** File repositories implement data persistence using JSON.

## Branching and Merge Workflow

The project uses Git for version control and a branch-based development workflow.

- `main` contains the stable version of the application.
- `development` is used for development and integration.
- Features and improvements are committed to the development branch.
- After testing, development is merged into main using a merge commit.

To inspect the commit history:

```bash
git log --oneline --graph --all
```

## Requirements

- Python 3.10 or later
- No external Python packages required

## Future Improvements

- Add unit tests using `unittest` or `pytest`.
- Add timestamps for request creation and resolution.
- Implement request assignment to support staff.
- Introduce additional request status values such as IN_PROGRESS.
- Replace JSON storage with a relational database.
- Add logging for monitoring application activities.

---

**Built as a Python application demonstrating OOP, abstraction, layered architecture, repository pattern, exception handling, persistent storage, and role-based access control.**
