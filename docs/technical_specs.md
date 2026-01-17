# Technical Specs — Step 1 (DB & Models)

## Stack
- SQLite (single-file database)
- SQLAlchemy ORM (synchronous)

## Time handling
We use `datetime.now(timezone.utc)` (not `utcnow()`) to ensure timezone-aware UTC timestamps in code helpers.

## Import convention
All internal imports use `from src.<package>...` to match the project layout and ensure IDE resolution.

## Model design (architectural decision)
### Why `properties` and `user_traits` are separate tables
We intentionally avoid a JSON/blob column on `events`. Instead, we store them as separate 1:1 tables:

- `event_properties` (`EventProperties`)
- `user_traits` (`UserTraits`)

Benefits:
- Explicit schema aligned with the known payload shape.
- Easy querying and indexing (e.g., `failure_reason`, `attempt_number`, `marketing_opt_in`).
- Keeps audit/debug views simple and consistent.

### 1:1 mapping
Each `Event` has:
- exactly 0..1 `EventProperties`
- exactly 0..1 `UserTraits`

Enforced by `unique=True` on `event_id` in both tables.

## Relationships
- `Event` 1..1 `EventProperties` (optional, cascade delete-orphan)
- `Event` 1..1 `UserTraits` (optional, cascade delete-orphan)
- `SendRequest.event_id` and `Suppression.event_id` are optional links back to `events` for audit traceability.


# Technical Specs — Step 2 (Alembic Migrations)

## Goal
Introduce schema migrations using Alembic and create the initial database schema for:
- events
- event_properties
- user_traits
- send_requests
- suppressions

## Configuration approach
- Alembic reads DATABASE_URL from environment (loaded via .env).
- `alembic/env.py` calls `load_dotenv()` and uses DATABASE_URL if set, otherwise defaults to `sqlite:///./messaging.db`.
- `target_metadata` is set to `Base.metadata` from `src.marketing_messaging_service.infrastructure.database`.

## Why env.py overrides sqlalchemy.url
We avoid hardcoding DB URLs in `alembic.ini` so the same project works across:
- local dev
- CI
- different environments via env vars

## Server defaults in SQLite
We use `CURRENT_TIMESTAMP` for:
- events.created_at
- send_requests.decided_at
- suppressions.decided_at

This matches the ORM intention of “created/decided time is set by DB” while keeping SQLite-compatible defaults.

## How to run
- Create migration (optional stub):
  - `alembic revision -m "create initial tables"`
- Apply migrations:
  - `alembic upgrade head`


# Technical Specs — Step 3 (Repositories)

## Minimal Repository Approach
We keep only the absolutely necessary CRUD operations.

Repositories included:
- EventRepository
- SendRequestRepository
- SuppressionRepository

Each repository provides only:
- add()
- get_by_id() (events only)

We deliberately avoid predictive “fancy methods” such as exists(), get_latest(), etc.
Those will be added only if the Service Layer explicitly needs them.
This keeps the architecture minimal and avoids premature complexity.


# Technical Specs — Step 4 (Controller Layer + Application Structure)

## Architectural Change: endpoints.py
We moved FastAPI application creation into a dedicated module:
`src/marketing_messaging_service/controllers/endpoints.py`.

This module:
- creates the FastAPI app
- registers all routers (event_router, audit_router)
- exposes the `app` object for both uvicorn and tests
- contains the `/health` endpoint

Benefits:
- avoids circular imports
- cleanly separates "app assembly" from "service bootstrapping"
- supports both CLI (`uvicorn module:app`) and programmatic startup

## main.py as launcher
`main.py` now only contains:
- import of settings
- a uvicorn.run() call pointing to `endpoints:app`

This keeps the entrypoint clean and environment-driven.

## Controllers
Controllers remain thin and follow a synchronous, layered approach:
- Route definition
- Input validation via Pydantic
- Dependency injection of DB session
- Delegation to the Service layer (implementation in Step 5)

## Schemas
- EventIn mirrors the assignment's event payload
- EventPropertiesIn and UserTraitsIn represent optional nested objects
- AuditResponse schema matches the required audit output structure


# Technical Specs — Step 5.1 (EventProcessingService)

## Scope
This step introduces the first service in the Service Layer:
- EventProcessingService

Only event persistence is implemented in this step.
No rule evaluation, deduplication, suppression logic, or outbound send generation is included yet.

## Inputs
- `EventIn` (validated by controller via Pydantic)

## Responsibilities
EventProcessingService.process_event():
1. Create `Event` from payload:
   - user_id
   - event_type
   - event_timestamp
   - properties (dynamic JSON object stored on Event model)
2. Persist Event using `IEventRepository.add()`
3. Persist optional `UserTraits` (1:1) linked by event_id

## Transaction boundaries
- Repositories do not commit/rollback.
- DB session transaction lifecycle is controlled by request scope (controller dependency).

## Output
- Returns the persisted `Event` instance (primarily for internal chaining in future steps).

## Tests included
- Unit test for service persistence (Event + UserTraits).
- Controller test for POST /events returns accepted and persists rows.
