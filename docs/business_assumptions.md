# Business Assumptions — Step 1 (DB & Models)

Assumption 1: Event properties and user traits are stored as explicit columns (not JSON).
Justification: The assignment provides a clear, stable schema for these fields, and rules/dedup rely on querying them directly (e.g., failure_reason, attempt_number, marketing_opt_in).
