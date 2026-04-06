## ADDED Requirements

### Requirement: Ticket Status Values

The system SHALL define the following ticket statuses:

| Status | Description |
|--------|-------------|
| pending | Ticket created, waiting for handling |
| in_progress | Handler is actively working on the ticket |
| resolved | Handler has resolved the issue |
| closed | Ticket is closed (final state) |

### Requirement: Status Transition Rules

The system SHALL enforce valid status transitions based on the following rules:

| From | To | Allowed By |
|------|----|------------|
| pending | in_progress | Assignee only |
| pending | closed | Creator or Admin |
| in_progress | resolved | Assignee only |
| in_progress | pending | Assignee only |
| resolved | closed | Creator or Admin |
| resolved | in_progress | Assignee only |
| closed | (none) | Final state, no transitions allowed |

#### Scenario: Valid status transition
- **WHEN** assignee changes status from "pending" to "in_progress"
- **THEN** system updates the ticket status
- **AND** system records status change in status history
- **AND** system creates audit log entry

#### Scenario: Invalid status transition
- **WHEN** user tries to change status from "pending" to "resolved" directly
- **THEN** system returns 400 error with message "Invalid status transition"

#### Scenario: Unauthorized status change
- **WHEN** non-assignee tries to change status from "pending" to "in_progress"
- **THEN** system returns 403 Forbidden

#### Scenario: Change status on closed ticket
- **WHEN** user tries to change status of a closed ticket
- **THEN** system returns 400 error with message "Cannot change status of closed ticket"

### Requirement: Status History

The system SHALL maintain a complete history of all status changes for each ticket.

#### Scenario: Record status history
- **WHEN** ticket status changes
- **THEN** system creates a new status_history record
- **AND** record includes: ticket_id, from_status, to_status, changed_by, changed_at

### Requirement: Get Status History

The system SHALL allow users to view the complete status history of a ticket.

#### Scenario: View status history
- **WHEN** user with access to ticket requests status history
- **THEN** system returns chronological list of all status changes
- **AND** includes who made each change and when
