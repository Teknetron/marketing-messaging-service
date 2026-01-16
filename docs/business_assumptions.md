# Business Assumptions — Step 1 (DB & Models)

Assumption 1: Event properties and user traits are stored as explicit columns (not JSON).
Justification: The assignment provides a clear, stable schema for these fields, and rules/dedup rely on querying them directly (e.g., failure_reason, attempt_number, marketing_opt_in).

# Business Assumptions — Step 2 (Migrations)

No business logic was introduced in Step 2.

Assumption 1: created_at/decided_at are set by the database using CURRENT_TIMESTAMP.
Justification: These timestamps represent persistence-time audit fields, and DB-side defaults avoid missing timestamps if a service forgets to set them.
