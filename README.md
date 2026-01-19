# Marketing Messaging Service 📬

A backend service that processes behavioral events and triggers rule-based marketing messages with deduplication and audit logging.

## Table of Contents

### Main Documentation
- [Tech Stack 🛠️](#tech-stack-️)
- [How to Run 🚀](#how-to-run-)
  - [Environment Setup](#environment-setup)
  - [Launch Service](#launch-service)
- [Assumptions 📄](#-assumptions)
- [API Documentation 📖](#api-documentation-)
- [Example API Usage 📡](#example-api-usage-)
  - [POST Event - Payment Failed Example 💳](#post-event---payment-failed-example-)
  - [GET Audit - View Decision History 📋](#get-audit---view-decision-history-)
- [Rule Configuration ⚙️](#rule-configuration-️)
- [Architecture Notes 🏗️](#architecture-notes-️)
  - [Database Connectivity 💾](#database-connectivity-)
  - [Timestamp Handling ⏰](#timestamp-handling-)
  - [Type Safety 🔒](#type-safety-)
  - [Clean Architecture 🎯](#clean-architecture-)

### Architecture Documentation
- [C4 Level 1: System Context 🌍](#c4-level-1-system-context-)
- [C4 Level 2: Container Diagram 📦](#c4-level-2-container-diagram-)
- [Key Architectural Patterns 📐](#key-architectural-patterns-)
- [Database Schema Overview 🗄️](#database-schema-overview-️)
- [Technology Stack Details 🛠️](#technology-stack-details-️)

---

## Tech Stack 🛠️

- **Framework**: FastAPI
- **Database**: SQLite, (SQLAlchemy 2.0 with `Mapped` types for type safety)  
- **Validation**: Pydantic v2 for request/response models
- **Configuration**: YAML-based rule definitions
- **Database**: SQLite (configurable to PostgreSQL/other databases)
- **Timestamps**: Timezone-aware UTC handling throughout

## How to Run 🚀

### Environment Setup

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Optional environment variables**:
   ```bash
   # Create .env file (optional)
   API_HOST=127.0.0.1
   API_PORT=8000
   DATABASE_URL=sqlite:///./messaging.db  # Default path
   ```

### Launch Service

```bash
python main.py
```

The service will start on `http://127.0.0.1:8000` with automatic reload enabled for development.

**Note**: When messages are triggered, they will be written to `messages.txt` in the root directory as a stub implementation of the messaging provider.

##  📄 Assumptions

### 🧱 Events & Traits Stored as Explicit Columns (Not JSON)

Event properties and user traits are saved as **explicit SQL columns**,
not JSON blobs.\
This enables direct querying, indexing, and predictable rule evaluation.

------------------------------------------------------------------------

### 📜 `rules.yaml` as the Single Source of Truth

All messaging logic, triggers, conditions, and suppression modes are
defined in **`rules.yaml`**.\
The code does **not** embed business logic.

------------------------------------------------------------------------

### 🎯 First-Matching-Rule Wins

Rule evaluation is **top-down**.\
The **first** rule that matches the event and its traits becomes the
active decision.\
Ordering in the YAML file matters.

------------------------------------------------------------------------

### 🔍 Audit Is for Explainability (Not Analytics)

Audit logs are designed for:\
- debugging\
- transparency\
- explaining why a user did or didn't get a message

Audit is **not** intended for analytics, reporting, or modeling.

------------------------------------------------------------------------

### 🕒 Event Timeline Uses Server-Side `created_at`

The meaningful processing timeline is based on the **server-side**
timestamp (`created_at`) written by the database, not the timestamp
provided by the event producer.

------------------------------------------------------------------------

### 🚫 Suppression Modes Are Limited

Only two suppression modes exist:

-   **`once_ever`** → Send only once in the user's lifetime\
-   **`once_per_calendar_day`** → Send at most once per UTC calendar day

No other frequency or throttling rules are considered.

------------------------------------------------------------------------

### 📆 Calendar-Day Logic Uses Event Timestamp

"Calendar day" calculations for suppression use the **event's own
timestamp**, not the server's `created_at` or the request arrival time.

------------------------------------------------------------------------

### 🔁 Prior-Event Checks Use Only the Most Recent Event

When evaluating conditions like "within 24 hours after signup," the
system checks **only the latest matching prior event**, not the full
event history.

------------------------------------------------------------------------

### 📦 Only Some Event Types Are Expected

The system assumes only the known event types from the assignment will
ever arrive (e.g., `signup_completed`, `payment_failed`, etc.).\
Unexpected event types are not part of rule evaluation.

------------------------------------------------------------------------

### 🧊 `rules.yaml` Is Static (Updated Only via Deployment)

Rules are treated as **static configuration**.\
Changes require redeployment or a service restart; there is no dynamic
or runtime rule reloading.

------------------------------------------------------------------------

### 📥 Properties Payload Is Trusted & Stored Raw

The `properties` dictionary from inbound events is:

-   accepted without deep validation,\
-   stored as-is,\
-   used directly for rule evaluation.

The service assumes the producer sends clean, well-formed data.

------------------------------------------------------------------------

### ➡️ Suppression & Sending Are Sequential (Not Atomic)

Suppression checks and message sending follow a **read → decide →
write** sequence.\
This process is **not atomic**, meaning:

-   two parallel requests might both pass suppression\
-   send logs and decisions can race\
-   DB inserts are not locked together

Atomic consistency is out of scope for the initial MVP.



## API Documentation 📖

Once running, visit `http://127.0.0.1:8000/docs` for interactive Swagger documentation.

## Example API Usage 📡

### POST Event - Payment Failed Example 💳

Process a payment failure event with user traits and properties:

```http
POST http://127.0.0.1:8000/events/
Content-Type: application/json

{
  "user_id": "user_12345",
  "event_type": "payment_failed",
  "event_timestamp": "2024-01-15T10:30:00Z",
  "properties": {
    "failure_reason": "INSUFFICIENT_FUNDS",
    "attempt_number": 1,
    "amount": 29.99,
    "currency": "USD"
  },
  "user_traits": {
    "email": "john.doe@example.com",
    "country": "US",
    "marketing_opt_in": true,
    "risk_segment": "low"
  }
}
```

**Expected Response**:
```json
{
  "event_id": 123,
  "user_id": "user_12345",
  "event_type": "payment_failed",
  "matched_rule": "insufficient_funds_email",
  "action_type": "send",
  "template_name": "INSUFFICIENT_FUNDS_EMAIL",
  "channel": "email",
  "outcome": "allow",
  "reason": "Rule matched and suppression check passed"
}
```

### GET Audit - View Decision History 📋

Retrieve complete audit trail for a user:

```http
GET http://127.0.0.1:8000/audit/user_12345
```

**Expected Response**:
```json
{
  "user_id": "user_12345",
  "decisions": [
    {
      "event_id": 123,
      "event_type": "payment_failed",
      "event_timestamp": "2024-01-15T10:30:00Z",
      "matched_rule": "insufficient_funds_email",
      "action_type": "send",
      "template_name": "INSUFFICIENT_FUNDS_EMAIL",
      "outcome": "allow",
      "reason": "Rule matched and suppression check passed",
      "decision_timestamp": "2024-01-15T10:30:01Z"
    }
  ]
}
```

## Rule Configuration ⚙️

The service evaluates events against rules defined in `config/rules.yaml`. Each rule specifies:

- **Trigger**: Which event type activates the rule
- **Conditions**: User traits and event property filters  
- **Action**: Message template and delivery channel
- **Suppression**: Deduplication logic (none, once_ever, once_per_calendar_day)

Example rule for payment failures:
```yaml
- name: "insufficient_funds_email"
  description: "Send insufficient funds email once per calendar day"
  enabled: true
  trigger:
    event_type: "payment_failed"
  conditions:
    all:
      - field: "properties.failure_reason"
        operator: "equals"
        value: "INSUFFICIENT_FUNDS"
  action:
    type: "send"
    template_name: "INSUFFICIENT_FUNDS_EMAIL"
    delivery_method: "email"
  suppression:
    mode: "once_per_calendar_day"
```

## Architecture Notes 🏗️

### Database Connectivity 💾
- **Default**: SQLite database at `./messaging.db`
- **Production**: Configure `DATABASE_URL` environment variable for PostgreSQL
- **Migrations**: Managed via Alembic (see `alembic/` directory)

### Timestamp Handling ⏰
All timestamps are stored and processed as timezone-aware UTC `datetime` objects, ensuring consistency across different deployment environments and compliance with modern Python standards.

### Type Safety 🔒
The codebase uses SQLAlchemy 2.0 `Mapped[Type]` annotations throughout for compile-time type checking and improved IDE support, following modern Python typing best practices.

### Clean Architecture 🎯
The service implements a layered architecture pattern:
- **Controllers**: HTTP request/response handling
- **Services**: Business logic and orchestration  
- **Repositories**: Data access layer with clean interfaces
- **Models**: SQLAlchemy entities with proper relationships

This separation enables easy testing, maintainability, and future scaling of the messaging infrastructure.



# Marketing Messaging Service - C4 Architecture Documentation 🏗️

This document provides comprehensive C4-style architecture diagrams for the Marketing Messaging Service, showing the system from different levels of abstraction.

## C4 Level 1: System Context 🌍

Shows external actors and systems that interact with our service.

```mermaid
graph TB
    subgraph External_Actors [" "]
        growth_team[👥 Growth Team<br/>Investigates why users<br/>did not receive messages]
        cx_team[👥 CX Team<br/>Responds to high-risk<br/>payment alerts]
    end
    
    subgraph External_Systems [" "]
        analytics[🔌 Analytics Platform<br/>Sends behavioral events<br/>Segment, mParticle, etc.]
        provider[📧 Messaging Provider<br/>Delivers emails/SMS<br/>Iterable, Braze<br/>Stubbed in implementation]
    end
    
    subgraph Internal_System [" "]
        messaging_service[⚙️ Marketing Messaging Service<br/>Processes behavioral events<br/>Evaluates rules, applies suppression<br/>Triggers messages, maintains audit trail]
    end
    
    %% Data flow connections
    analytics -->|POST /events<br/>JSON payload with user traits| messaging_service
    messaging_service -->|Send Message<br/>Stubbed to messages.txt| provider
    messaging_service -->|GET /audit/user_id<br/>View decision history| growth_team
    messaging_service -->|GET /audit/user_id<br/>Check alerts and outcomes| cx_team

    classDef external fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef internal fill:#f3e5f5,stroke:#4a148c,stroke-width:3px
    classDef actors fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px

    class analytics,provider external
    class messaging_service internal
    class growth_team,cx_team actors
```

**Key System Boundaries:**
- **Internal**: FastAPI service, rule evaluation engine, suppression logic, SQLite persistence
- **External**: Analytics platform (event source), messaging providers (delivery stub)
- **Actors**: Growth and CX teams consuming audit trails for analysis

---

## C4 Level 2: Container Diagram 📦

Shows the internal architecture with layered components and their interactions.

```mermaid
graph TB
    analytics[🔌 Analytics Platform]
    teams[👥 Internal Teams]
    
    subgraph API_Layer [🌐 API Layer]
        fastapi[⚙️ FastAPI Application]
        event_controller[📥 Event Controller]
        audit_controller[📊 Audit Controller]
    end
    
    subgraph Service_Layer [🔧 Service Layer]
        event_processing[⚙️ EventProcessingService]
        rule_evaluation[🎯 RuleEvaluationService]
        suppression[🚫 SuppressionService]
        audit_service[📋 AuditService]
    end
    
    subgraph Repository_Layer [💾 Repository Layer]
        event_repo[📝 EventRepository]
        send_repo[📤 SendRequestRepository]
        suppress_repo[🚫 SuppressionRepository]
        decision_repo[📊 DecisionRepository]
    end
    
    subgraph Infrastructure_Layer [🏗️ Infrastructure Layer]
        database[(💾 SQLite Database)]
        rules_config[📋 Rules Configuration]
        fake_provider[📧 FakeMessagingProvider]
    end
    
    subgraph Models [📋 Models]
        decisions[📊 Decisions]
        events[📝 Events]
        send_requests[📤 SendRequests]
        user_traits[👤 UserTraits]
        suppressions[🚫 Suppressions]
    end
    
    provider[📧 Messaging Provider]
    
    %% External connections
    analytics --> event_controller
    teams --> audit_controller
    
    %% API Layer connections
    fastapi --> event_controller
    fastapi --> audit_controller
    
    %% Controller to Service connections
    event_controller --> event_processing
    audit_controller --> audit_service
    
    %% Service orchestration
    event_processing --> rule_evaluation
    event_processing --> suppression
    event_processing --> fake_provider
    
    %% Service to Repository connections
    event_processing --> event_repo
    event_processing --> send_repo
    event_processing --> suppress_repo
    event_processing --> decision_repo
    audit_service --> decision_repo
    
    %% Repository to Database connections
    event_repo --> database
    send_repo --> database
    suppress_repo --> database
    decision_repo --> database
    
    %% Database to Models
    database --> Models
    
    %% Configuration dependencies
    rule_evaluation --> rules_config
    
    %% External provider connection
    fake_provider --> provider

    classDef external fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef service fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef repository fill:#fce4ec,stroke:#ad1457,stroke-width:2px
    classDef infrastructure fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef model fill:#fff8e1,stroke:#f57f17,stroke-width:2px

    class analytics,teams,provider external
    class fastapi,event_controller,audit_controller api
    class event_processing,rule_evaluation,suppression,audit_service service
    class event_repo,send_repo,suppress_repo,decision_repo repository
    class database,rules_config,fake_provider infrastructure
    class decisions,events,send_requests,user_traits,suppressions model
```

---

## Key Architectural Patterns 📐

### 1. Layered Architecture 🏢
- **Controllers**: HTTP request/response handling with dependency injection
- **Services**: Business logic orchestration with clear responsibilities  
- **Repositories**: Data access abstraction with interface contracts
- **Models**: Rich domain objects with proper SQLAlchemy relationships

### 2. Dependency Injection 💉
All services receive their dependencies via constructor injection, enabling:
- **Testability**: Easy mocking of dependencies
- **Flexibility**: Swappable implementations (e.g., different messaging providers)
- **Separation of Concerns**: Clear boundaries between layers

### 3. Interface Segregation 🔌
Repository interfaces define clean contracts:
- `IEventRepository`: Event persistence and querying
- `ISendRequestRepository`: Delivery tracking with suppression queries
- `ISuppressionRepository`: Suppression event logging
- `IDecisionRepository`: Complete audit trail persistence
- `IMessagingProvider`: External messaging abstraction

### 4. Domain-Driven Design 🎯
Rich domain models with clear relationships:
- **Event** ← **UserTraits** (optional 1:1)
- **Decision** → **Event** (FK relationship)
- **SendRequest** → **Event** (FK relationship)  
- **Suppression** → **Event** (FK relationship)

### 5. Configuration as Code ⚙️
YAML-based rule configuration enables:
- **Runtime flexibility**: No code changes for new campaigns
- **Business user empowerment**: Growth teams can modify rules
- **Version control**: Rule changes tracked in git

---

## Database Schema Overview 🗄️

```mermaid
erDiagram
    events {
        int id PK
        varchar user_id
        varchar event_type
        datetime event_timestamp
        json properties
        datetime created_at
    }
    
    user_traits {
        int id PK
        int event_id FK
        varchar email
        varchar country
        boolean marketing_opt_in
        varchar risk_segment
    }
    
    decisions {
        int id PK
        varchar user_id
        int event_id FK
        varchar event_type
        varchar matched_rule
        varchar action_type
        varchar outcome
        varchar reason
        varchar template_name
        varchar channel
        datetime created_at
    }
    
    send_requests {
        int id PK
        varchar user_id
        int event_id FK
        datetime event_timestamp
        varchar template_name
        varchar channel
        varchar reason
        datetime created_at
    }
    
    suppressions {
        int id PK
        varchar user_id
        int event_id FK
        varchar template_name
        varchar suppression_reason
        datetime created_at
    }
    
    events ||--o{ user_traits : "has optional"
    events ||--o{ decisions : "generates"  
    events ||--o{ send_requests : "may trigger"
    events ||--o{ suppressions : "may suppress"
```

---

## Technology Stack Details 🛠️

### Core Framework
- **FastAPI**: Async web framework with automatic OpenAPI documentation
- **SQLAlchemy 2.0**: Modern ORM with `Mapped[Type]` annotations for type safety
- **Pydantic**: Request/response validation with Python type hints
- **Alembic**: Database migration management

### Infrastructure  
- **SQLite**: Default database (configurable to PostgreSQL)
- **Poetry**: Dependency management and virtual environments
- **YAML**: Human-readable configuration for marketing rules

### Development
- **Modern Python 3.11+**: Leveraging union types (`str | None`) and enhanced typing
- **Clean Architecture**: Dependency inversion with interface abstractions
- **UTC Timestamps**: Timezone-aware datetime handling throughout