# Business Assumptions — Step 1 (DB & Models)

Assumption 1: Event properties and user traits are stored as explicit columns (not JSON).
Justification: The assignment provides a clear, stable schema for these fields, and rules/dedup rely on querying them directly (e.g., failure_reason, attempt_number, marketing_opt_in).

# Business Assumptions — Step 2 (Migrations)

No business logic was introduced in Step 2.

Assumption 1: created_at/decided_at are set by the database using CURRENT_TIMESTAMP.
Justification: These timestamps represent persistence-time audit fields, and DB-side defaults avoid missing timestamps if a service forgets to set them.


# Business Assumptions — Step 3

Assumption 1: Only add() and (for events) get_by_id() are required at this stage.
Justification: We are designing the repository layer to be minimal and grow only when real service requirements emerge.


# Business Assumptions — Step 4 (Controllers)

Assumption 1: Application creation should be isolated from runtime bootstrap.
Justification: Following clean architecture and FastAPI best practices, keeping `app = FastAPI()` inside a dedicated module simplifies testing, improves modularity, and avoids circular dependencies.

Assumption 2: Controllers remain purely responsible for request validation and routing.
Justification: The service layer will implement all business logic. Controllers should stay thin and minimal in accordance with SOLID (Single Responsibility Principle).

Assumption 3: The /health endpoint is part of endpoints.py, not main.py.
Justification: Health checks belong to the HTTP API surface, not to the bootstrap code.


# Business Assumptions — Step 5.1

No business decisions introduced in this step.


# Business Assumptions — Step 5.2

No new explicit business assumptions were introduced in this step.
Rules are evaluated exactly as written in rules.yaml.