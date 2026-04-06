## ADDED Requirements

### Requirement: Create Ticket

The system SHALL allow authenticated users to create new tickets with title, description, and priority.

#### Scenario: Successful ticket creation
- **WHEN** authenticated user submits valid title, description, and priority
- **THEN** system creates a new ticket with status "pending"
- **AND** system assigns ticket_id and created_at timestamp
- **AND** system returns the created ticket

#### Scenario: Missing required fields
- **WHEN** user submits ticket without title
- **THEN** system returns 422 validation error

### Requirement: List Tickets

The system SHALL allow users to list tickets with pagination and filtering.

#### Scenario: List all tickets (admin/assignee)
- **WHEN** admin or assigned user requests ticket list
- **THEN** system returns paginated tickets (default: 20 per page)
- **AND** includes total count and pagination metadata

#### Scenario: Filter by status
- **WHEN** user requests tickets filtered by status "pending"
- **THEN** system returns only tickets with status "pending"

#### Scenario: Filter by priority
- **WHEN** user requests tickets filtered by priority "high"
- **THEN** system returns only tickets with priority "high"

### Requirement: Get Ticket Detail

The system SHALL allow users to view detailed ticket information.

#### Scenario: Get own or assigned ticket
- **WHEN** user requests ticket they created or are assigned to
- **THEN** system returns full ticket details including status history

#### Scenario: Get unauthorized ticket
- **WHEN** user requests ticket they did not create and are not assigned to
- **THEN** system returns 403 Forbidden

### Requirement: Update Ticket

The system SHALL allow users to update ticket title, description, and priority.

#### Scenario: Update own ticket
- **WHEN** ticket creator updates their ticket
- **THEN** system updates the ticket
- **AND** system records the update in audit log

#### Scenario: Update assigned ticket
- **WHEN** assignee updates their assigned ticket
- **THEN** system updates the ticket

#### Scenario: Update without permission
- **WHEN** user updates ticket they don't have access to
- **THEN** system returns 403 Forbidden

### Requirement: Delete Ticket

The system SHALL allow ticket creators to delete their own tickets.

#### Scenario: Delete own ticket
- **WHEN** ticket creator deletes their ticket
- **THEN** system marks ticket as deleted (soft delete)
- **AND** system records deletion in audit log

#### Scenario: Delete others' ticket
- **WHEN** user deletes another user's ticket
- **THEN** system returns 403 Forbidden

### Requirement: Ticket Fields

The system SHALL define ticket with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| title | String(200) | Yes | Ticket title |
| description | Text | Yes | Detailed description |
| priority | Enum | Yes | low, medium, high |
| status | Enum | Yes | pending, in_progress, resolved, closed |
| creator_id | UUID | Yes | User who created the ticket |
| assignee_id | UUID | No | Assigned user |
| created_at | DateTime | Yes | Creation timestamp |
| updated_at | DateTime | Yes | Last update timestamp |
| deleted_at | DateTime | No | Soft delete timestamp |
