# Step Summary — Step 1 (DB & Models)

## What was done
- Added synchronous SQLAlchemy bootstrap (`engine`, `SessionLocal`, `create_session()`).
- Updated UTC helper to use `datetime.now(timezone.utc)`.
- Implemented ORM models:
  - Event
  - EventProperties (explicit columns: amount, attempt_number, failure_reason)
  - UserTraits (explicit columns: email, country, marketing_opt_in, risk_segment)
  - SendRequest
  - Suppression
- Enforced 1:1 mapping between Event and properties/traits using unique event_id.

## PlantUML (Models Diagram)
```plantuml
@startuml
skinparam linetype ortho
hide methods

class Event {
  +id: int
  +user_id: str
  +event_type: str
  +event_timestamp: datetime
  +created_at: datetime
}

class EventProperties {
  +id: int
  +event_id: int (unique)
  +amount: float?
  +attempt_number: int?
  +failure_reason: str?
}

class UserTraits {
  +id: int
  +event_id: int (unique)
  +email: str?
  +country: str?
  +marketing_opt_in: bool?
  +risk_segment: str?
}

class SendRequest {
  +id: int
  +user_id: str
  +event_id: int?
  +template_name: str
  +channel: str
  +reason: text
  +decided_at: datetime
}

class Suppression {
  +id: int
  +user_id: str
  +event_id: int?
  +template_name: str
  +suppression_reason: text
  +decided_at: datetime
}

Event "1" o-- "0..1" EventProperties : properties
Event "1" o-- "0..1" UserTraits : user_traits
Event "0..1" <-- SendRequest : event_id
Event "0..1" <-- Suppression : event_id

@enduml
```


# Step Summary — Step 2 (Alembic Migrations)

## What was done
- Wired Alembic to SQLAlchemy metadata (`Base.metadata`) so Alembic understands our schema.
- Loaded DATABASE_URL from `.env` in Alembic runtime.
- Added initial migration `create_initial_tables` creating all required tables and indexes.
- Implemented a clean downgrade reversing table creation order.


# Step Summary — Step 3 (Minimal Repositories)

## What was done
- Introduced a minimal repository layer.
- Removed event_properties and user_traits repositories.
- Removed all prediction-based query methods.
- Added only add() for all entities and get_by_id() for Event.
- Prepared the layer for expansion during Service implementation.

## UML
```plantuml
@startuml
interface IEventRepository
interface ISendRequestRepository
interface ISuppressionRepository

class EventRepository
class SendRequestRepository
class SuppressionRepository

IEventRepository <|.. EventRepository
ISendRequestRepository <|.. SendRequestRepository
ISuppressionRepository <|.. SuppressionRepository
@enduml
```

# Step Summary — Step 4 (Controller Layer)

## What was done
- Implemented controllers: EventController and AuditController.
- Added Pydantic schemas for event ingestion and audit responses.
- Assembled all routers inside `controllers/endpoints.py`.
- Moved FastAPI app creation to `endpoints.py`.
- Updated `main.py` to serve purely as a uvicorn launcher.
- Ensured dependency injection for DB sessions (synchronous).

## Final File Structure
```
controllers/
├── audit_controller.py
├── endpoints.py
└── event_controller.py
schemas/
├── audit.py
└── event.py
main.py
```

## Updated UML
```plantuml
@startuml
hide methods
skinparam linetype ortho

package "HTTP Layer" {
  class Endpoints {
    +app: FastAPI
  }
  class EventController
  class AuditController
}

Endpoints --> EventController
Endpoints --> AuditController

EventController --> "EventIn"
EventController --> "EventAccepted"

AuditController --> "AuditResponse"
@enduml
```

# Step Summary — Step 5.1 (Event Persistence)

## What Was Implemented
- Added EventProcessingService with the responsibility to persist:
  - Event including dynamic JSON properties
  - UserTraits (1:1) via ORM cascade
- Integrated service into POST /events controller
- Implemented and validated service behavior through tests

## Key Change
UserTraits are now persisted by setting `event.user_traits = UserTraits(...)` and allowing SQLAlchemy to cascade persistence.

## Completed Tests
- Service-level test confirming event + properties + traits persistence and relationship integrity
- Controller test ensuring the endpoint returns `{"status": "accepted"}` and data is saved properly

## PlantUML
```plantuml
@startuml
skinparam linetype ortho
hide methods

package "Controller Layer" {
  class EventController
}

package "Service Layer" {
  class EventProcessingService
}

package "Repository Layer" {
  interface IEventRepository
  class EventRepository
}

package "Models" {
  class Event
  class UserTraits
}

EventController --> EventProcessingService : process_event()
EventProcessingService --> IEventRepository : add(event)
IEventRepository <|.. EventRepository

Event --> UserTraits : 1:1 (cascade)
EventRepository --> Event

@enduml
```