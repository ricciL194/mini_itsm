## ADDED Requirements

### Requirement: List Users

The system SHALL allow admins to list all users with pagination.

#### Scenario: Admin lists users
- **WHEN** admin requests user list
- **THEN** system returns paginated list of users
- **AND** excludes soft-deleted users

#### Scenario: Non-admin lists users
- **WHEN** regular user requests user list
- **THEN** system returns 403 Forbidden

### Requirement: Get User Detail

The system SHALL allow admins to view detailed user information.

#### Scenario: Admin views user detail
- **WHEN** admin requests user details by ID
- **THEN** system returns user_id, username, email, role, created_at, is_active

#### Scenario: Get non-existent user
- **WHEN** admin requests details of non-existent user
- **THEN** system returns 404 error

### Requirement: Update User Role

The system SHALL allow admins to update user roles (user ↔ admin).

#### Scenario: Promote user to admin
- **WHEN** admin changes user role from "user" to "admin"
- **THEN** system updates the user's role
- **AND** system creates audit log entry

#### Scenario: Demote admin to user
- **WHEN** admin changes admin role from "admin" to "user"
- **THEN** system updates the user's role
- **AND** system creates audit log entry

#### Scenario: Admin cannot demote self
- **WHEN** admin tries to change their own role
- **THEN** system returns 400 error with message "Cannot change your own role"

### Requirement: Deactivate User

The system SHALL allow admins to deactivate users (soft delete).

#### Scenario: Deactivate user
- **WHEN** admin deactivates a user
- **THEN** system sets is_active to false
- **AND** user cannot log in
- **AND** system creates audit log entry

#### Scenario: Deactivated user login attempt
- **WHEN** deactivated user attempts to login
- **THEN** system returns 401 error with message "Account is deactivated"

#### Scenario: Admin cannot deactivate self
- **WHEN** admin tries to deactivate their own account
- **THEN** system returns 400 error with message "Cannot deactivate your own account"

### Requirement: Reactivate User

The system SHALL allow admins to reactivate deactivated users.

#### Scenario: Reactivate user
- **WHEN** admin reactivates a user
- **THEN** system sets is_active to true
- **AND** user can log in again
- **AND** system creates audit log entry

### Requirement: User Fields

The system SHALL define user with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| username | String(50) | Yes | Unique username |
| email | String(255) | Yes | Unique email address |
| password_hash | String | Yes | Bcrypt hashed password |
| role | Enum | Yes | user, admin |
| is_active | Boolean | Yes | Account active status |
| created_at | DateTime | Yes | Creation timestamp |
| updated_at | DateTime | Yes | Last update timestamp |
| deleted_at | DateTime | No | Soft delete timestamp |
