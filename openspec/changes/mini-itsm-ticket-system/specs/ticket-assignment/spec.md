## ADDED Requirements

### Requirement: Assign Ticket to Handler

The system SHALL allow ticket creators or admins to assign a ticket to a handler.

#### Scenario: Assign ticket to user
- **WHEN** creator or admin assigns ticket to a valid user
- **THEN** system updates assignee_id on the ticket
- **AND** system creates audit log entry for assignment

#### Scenario: Assign to non-existent user
- **WHEN** user assigns ticket to a user_id that doesn't exist
- **THEN** system returns 404 error

#### Scenario: Assign without permission
- **WHEN** regular user tries to assign someone else's ticket
- **THEN** system returns 403 Forbidden

### Requirement: Reassign Ticket

The system SHALL allow ticket creators or admins to reassign a ticket to a different handler.

#### Scenario: Reassign ticket
- **WHEN** creator or admin reassigns ticket from user A to user B
- **THEN** system updates assignee_id to user B
- **AND** system creates audit log entry showing reassignment

### Requirement: Unassign Ticket

The system SHALL allow ticket creators or admins to unassign a ticket (remove the handler).

#### Scenario: Unassign ticket
- **WHEN** creator or admin removes assignee from ticket
- **THEN** system sets assignee_id to null
- **AND** system creates audit log entry for unassignment

### Requirement: Get Assigned Tickets

The system SHALL allow users to view all tickets assigned to them.

#### Scenario: Get assigned tickets
- **WHEN** user requests their assigned tickets
- **THEN** system returns list of tickets where assignee_id equals current user
- **AND** includes pagination

### Requirement: Self-Assign Ticket

The system SHALL allow handlers to self-assign unassigned tickets.

#### Scenario: Self-assign ticket
- **WHEN** user assigns a ticket to themselves (assignee_id set to current user)
- **THEN** system updates the ticket assignment
- **AND** system creates audit log entry
