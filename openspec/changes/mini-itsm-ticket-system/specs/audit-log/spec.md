## ADDED Requirements

### Requirement: Audit Log Coverage

The system SHALL record the following actions in the audit log:

| Action | Description | Trigger |
|--------|-------------|---------|
| user.register | User registration | POST /api/auth/register |
| user.login | User login | POST /api/auth/login |
| user.logout | User logout | POST /api/auth/logout |
| user.refresh_token | Token refresh | POST /api/auth/refresh |
| ticket.create | Ticket creation | POST /api/tickets |
| ticket.update | Ticket update | PUT /api/tickets/{id} |
| ticket.delete | Ticket deletion | DELETE /api/tickets/{id} |
| ticket.assign | Ticket assignment | POST /api/tickets/{id}/assign |
| ticket.unassign | Ticket unassignment | DELETE /api/tickets/{id}/assign |
| ticket.status_change | Status change | PATCH /api/tickets/{id}/status |

### Requirement: Audit Log Fields

The audit log SHALL record the following information:

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| user_id | UUID | User who performed the action |
| action | String | Action identifier |
| resource_type | String | Type of resource (e.g., ticket, user) |
| resource_id | UUID | ID of the affected resource |
| old_value | JSON | Previous value (for updates) |
| new_value | JSON | New value |
| ip_address | String | Client IP address |
| user_agent | String | Client user agent |
| created_at | DateTime | Timestamp of the action |

### Requirement: Query Audit Logs

The system SHALL allow admins to query audit logs with filtering and pagination.

#### Scenario: Query all logs (admin)
- **WHEN** admin requests audit logs
- **THEN** system returns paginated list of all logs
- **AND** ordered by created_at descending

#### Scenario: Filter by action
- **WHEN** admin requests logs filtered by action "ticket.create"
- **THEN** system returns only logs with action "ticket.create"

#### Scenario: Filter by user
- **WHEN** admin requests logs filtered by user_id
- **THEN** system returns only logs for that user

#### Scenario: Filter by date range
- **WHEN** admin requests logs with start_date and end_date
- **THEN** system returns only logs within that range

### Requirement: Get Resource Audit History

The system SHALL allow users to view the audit history of a specific resource.

#### Scenario: Get ticket audit history
- **WHEN** user with ticket access requests its audit history
- **THEN** system returns all audit logs for that ticket
- **AND** ordered chronologically

#### Scenario: Get unauthorized resource audit
- **WHEN** user requests audit history of a resource they don't have access to
- **THEN** system returns 403 Forbidden
