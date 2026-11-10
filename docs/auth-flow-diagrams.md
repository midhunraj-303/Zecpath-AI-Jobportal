# Zecpath ATS – Authentication Flow Diagrams

## 1. Overview

Zecpath uses Django REST Framework (DRF) with JSON Web Token (JWT) authentication.

The authentication system supports three user roles:

- **ADMIN** – System administrator
- **EMPLOYER** – Employer account
- **CANDIDATE** – Candidate account

Newly registered users must verify their email address before accessing protected APIs.

## 2. User Registration and Email Verification

This flow describes how a new candidate or employer creates an account and verifies their email address.

```mermaid
flowchart TD
    A[User submits registration details] --> B[Validate registration data]
    B --> C{Valid data?}

    C -->|No| D[Return validation errors]
    C -->|Yes| E[Create user account]

    E --> F[Set is_active = False]
    F --> G[Set is_verified = False]
    G --> H[Generate email verification token]
    H --> I[Send verification email]

    I --> J[User opens verification link]
    J --> K[Validate verification token]

    K --> L{Token valid?}
    L -->|No| M[Return verification error]
    L -->|Yes| N[Activate user account]

    N --> O[Set is_active = True]
    O --> P[Set is_verified = True]
    P --> Q[Email verification completed]
```

**Important points:**

- Newly registered accounts are inactive and unverified.
- Verification tokens are time-sensitive.
- Invalid, expired or previously used tokens are rejected.
- The token is invalidated when relevant account information changes.

## 3. User Login and JWT Generation

After successful email verification, the user can log in.

```mermaid
flowchart TD
    A[User submits email and password] --> B[JWT Login API]
    B --> C[Validate credentials]

    C --> D{Credentials valid?}
    D -->|No| E[Return authentication error]
    D -->|Yes| F[Check account status]

    F --> G{Active and verified?}
    G -->|No| H[Reject login]
    G -->|Yes| I[Generate JWT tokens]

    I --> J[Access Token]
    I --> K[Refresh Token]

    J --> L[Return token response]
    K --> L
    L --> M[Client stores tokens securely]
```

**Login endpoint:**

`POST /api/accounts/login/`

**JWT configuration:**

| Setting | Value |
|---|---|
| Access token lifetime | 30 minutes |
| Refresh token lifetime | 1 day |
| Authentication header | Bearer |
| Token rotation | Enabled |
| Blacklist after rotation | Enabled |

## 4. Authenticated API Request and Role-Based Access Control

The client sends its access token when accessing protected APIs.

```mermaid
flowchart TD
    A[Client requests protected API] --> B[Send Bearer Access Token]
    B --> C[JWT Authentication]

    C --> D{Token valid?}
    D -->|No| E[Return 401 Unauthorized]
    D -->|Yes| F[Identify authenticated user]

    F --> G[Check account status]
    G --> H{Active and verified?}

    H -->|No| I[Reject access]
    H -->|Yes| J[Check user role]

    J --> K{Required role matches?}
    K -->|No| L[Return 403 Forbidden]
    K -->|Yes| M[Execute API operation]

    M --> N[Return API response]
```

**Role-based permissions:**

| Permission class | Required role |
|---|---|
| `IsAdmin` | ADMIN |
| `IsEmployer` | EMPLOYER |
| `IsCandidate` | CANDIDATE |

Protected APIs also enforce resource ownership where applicable.

## 5. JWT Refresh Token Flow

When the access token expires, the client can request a new access token using its refresh token.

```mermaid
flowchart TD
    A[Access token expires] --> B[Client sends refresh token]
    B --> C[POST /api/accounts/token/refresh/]

    C --> D{Refresh token valid?}

    D -->|No| E[Return authentication error]
    D -->|Yes| F[Generate new access token]

    F --> G[Rotate refresh token]
    G --> H[Blacklist previous refresh token]
    H --> I[Return new tokens]
    I --> J[Client updates stored tokens]
    J --> K[Continue API requests]
```

**Important:** Refresh token rotation is enabled. The client must use the newly returned refresh token for subsequent refresh requests.

## 6. User Logout Flow

Zecpath uses refresh token blacklisting to prevent reuse of a logged-out session's refresh token.

```mermaid
flowchart TD
    A[User requests logout] --> B[Send access token]
    B --> C[Submit refresh token]

    C --> D[Validate refresh token]
    D --> E{Token valid and belongs to user?}

    E -->|No| F[Reject logout request]
    E -->|Yes| G[Blacklist refresh token]

    G --> H[Return logout confirmation]
```

**Important security considerations:**

- A user cannot blacklist another user's refresh token.
- A blacklisted refresh token cannot be reused.
- Existing access tokens remain valid until their expiration unless additional access-token revocation is implemented.

## 7. Authentication API Endpoints

| Operation | Method | Endpoint |
|---|---|---|
| Login | POST | `/api/accounts/login/` |
| Refresh token | POST | `/api/accounts/token/refresh/` |
| Logout | POST | `/api/accounts/logout/` |

Registration and email verification endpoints are documented in the API usage guide.

## 8. Security Summary

- JWT authentication is used for protected APIs.
- Email verification is required before account access.
- Access tokens expire after 30 minutes.
- Refresh tokens expire after one day.
- Refresh token rotation and blacklisting are enabled.
- Logout validates refresh-token ownership.
- Role-based permissions protect role-specific APIs.
- Resource ownership is enforced by the relevant API views.

---

**Project:** Zecpath ATS  
**Documentation:** Authentication Flow Diagrams  
**Technology:** Django, Django REST Framework, Simple JWT  
