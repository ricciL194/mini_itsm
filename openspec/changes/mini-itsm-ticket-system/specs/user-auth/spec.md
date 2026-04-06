## ADDED Requirements

### Requirement: User Registration

The system SHALL allow users to register with a unique username, email, and password.

#### Scenario: Successful registration
- **WHEN** user submits valid username, email, and password (min 8 characters)
- **THEN** system creates a new user account with hashed password
- **AND** system returns success message with user_id

#### Scenario: Duplicate email registration
- **WHEN** user submits an email that already exists
- **THEN** system returns 400 error with message "Email already registered"

#### Scenario: Weak password
- **WHEN** user submits password with less than 8 characters
- **THEN** system returns 422 validation error

### Requirement: User Login

The system SHALL authenticate users with email and password, returning JWT tokens.

#### Scenario: Successful login
- **WHEN** user submits correct email and password
- **THEN** system returns access_token (15 min expiry) and refresh_token (7 days expiry)

#### Scenario: Invalid credentials
- **WHEN** user submits wrong password
- **THEN** system returns 401 error with message "Invalid credentials"

#### Scenario: Non-existent user
- **WHEN** user submits email that does not exist
- **THEN** system returns 401 error with message "Invalid credentials"

### Requirement: Token Refresh

The system SHALL allow users to refresh access tokens using a valid refresh token.

#### Scenario: Successful token refresh
- **WHEN** user submits valid refresh_token
- **THEN** system returns new access_token and refresh_token
- **AND** old refresh_token is invalidated

#### Scenario: Expired refresh token
- **WHEN** user submits expired refresh_token
- **THEN** system returns 401 error

#### Scenario: Invalid refresh token
- **WHEN** user submits malformed refresh_token
- **THEN** system returns 401 error

### Requirement: User Logout

The system SHALL allow users to logout, invalidating their refresh token.

#### Scenario: Successful logout
- **WHEN** authenticated user requests logout
- **THEN** system invalidates the refresh token
- **AND** user cannot use the refresh token to obtain new access tokens

### Requirement: Get Current User

The system SHALL allow authenticated users to retrieve their profile information.

#### Scenario: Get own profile
- **WHEN** authenticated user requests their profile
- **THEN** system returns user_id, username, email, created_at

#### Scenario: Unauthorized request
- **WHEN** unauthenticated user requests profile
- **THEN** system returns 401 error
