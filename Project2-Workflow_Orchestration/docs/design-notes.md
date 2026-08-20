# Design Notes

- Chose an orchestration architecture instead of direct system-to-system communication to centralize business workflow while preserving system ownership.

- Kept each business system responsible only for the data it owns, preventing the orchestration layer from becoming another source of truth.

- Structured the workflow using small, single-purpose validation functions coordinated through a single orchestration function rather than embedding business rules inside one large method.

- Used guard clauses throughout validation functions to stop processing immediately when business rules fail, reducing nesting and making failure paths explicit.

- Combined patient ownership and active-status validation into a single function because both rules originate from the Patient Records system.

- Calculated appointment end times dynamically from appointment type metadata rather than storing appointment durations within incoming requests.

- Standardized internal date/time formatting using Python's datetime module while storing database values as text for consistent SQLite interoperability.

- Checked for duplicate appointments before provider availability to avoid unnecessary processing for requests that already exist.

- Used interval-overlap comparisons for provider scheduling conflicts instead of checking only identical appointment times.

- Generated primary keys deterministically using MAX(ID) + 1 because project data is reseeded for repeatable demonstrations rather than relying on AUTOINCREMENT behavior.

- Simulated a temporary Patient Records outage through configuration flags rather than random failures so retry behavior remains deterministic and repeatable during demonstrations.

- Implemented deferred request processing separately from the primary workflow so retry behavior remains isolated from normal business execution.

- Recorded business failures with user-oriented reconciliation guidance while treating temporary system outages as deferred operational events rather than validation failures.

- Included workflow reporting as part of the orchestration process to provide operational visibility into successful, failed, deferred, and retried requests.

- Deliberately modeled business processes before implementation details so the workflow diagrams remain applicable regardless of programming language or integration platform.

- Limited project scope to orchestration responsibilities and intentionally excluded authentication, API communication, transaction rollback, and background scheduling so the project remained focused on business workflow coordination.