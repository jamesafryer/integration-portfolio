# Design Notes

These notes capture implementation decisions, trade-offs, and observations made while developing Project 1. They are intended to document the reasoning behind the current design and identify areas for future expansion.

---

## Repeatable Testing

For repeatable testing, the seed script explicitly assigns CustomerIDs even though the production schema supports auto-incrementing identifiers. This allows deterministic recreation of synchronization scenarios.

---

## Synchronization Strategy

- Customer Management is treated as the system of record.
- Billing stores a local snapshot of customer information.
- Whole-record versioning was selected as an intentionally simple first implementation.

---

## Development Observations

- Designing algorithms in plain English before implementation significantly reduced coding complexity.
- Parameterized SQL queries improved readability while preventing SQL injection vulnerabilities.
- Seeding repeatable test data significantly simplified debugging and validation of synchronization behavior.
- Passing database resources explicitly into helper functions reduced hidden dependencies and improved code reuse.
- Refactoring working code into smaller helper functions improved readability without changing program behavior.
- Database transactions should only be committed after all intended changes complete successfully.
- Set operations provided a clean and efficient solution for identifying orphaned records.
- Designing synchronization logic in plain English before writing Python reduced implementation complexity.
- Returning structured dictionaries from synchronization functions proved significantly easier to extend than returning simple status strings, allowing the reporting layer to evolve without changing business logic.
- Separating synchronization logic from reporting responsibilities made the codebase easier to extend while keeping presentation concerns independent from processing logic.
- Exceptions became more useful when treated as carriers of information rather than program-ending errors, allowing the orchestration layer to decide whether to retry, defer, or report synchronization failures.
- Separating configuration values from runtime state made the outage simulation easier to understand while keeping demonstration-specific behavior isolated from the synchronization algorithm.
- Keeping documentation synchronized with implementation proved just as important as keeping code synchronized with changing requirements.
- Maintaining consistent data structures between processing stages simplified synchronization logic and reduced debugging complexity, particularly when implementing deferred retry processing.

---

## Future Enhancements

- Field-level version tracking
- API communication
- Persistent retry queue
- Configuration files