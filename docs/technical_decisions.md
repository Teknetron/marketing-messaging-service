# Technical Decisions

## Step 5.1 — Event properties stored as dynamic JSON
Decision: Store event `properties` as a dynamic JSON object on the Event model.
Rationale: Event properties can vary by event type and are not guaranteed to be stable; JSON storage avoids schema churn while keeping the event record self-contained.

## Step 5.1 — Keep SendRequest/Suppression linked to Event
Decision: Keep optional `event_id` on SendRequest and Suppression.
Rationale: Improves audit traceability by allowing deterministic linkage from a decision (send/suppress) back to the triggering event.

## Step 5.1 — Minimal repository methods
Decision: Keep repositories minimal (add / get_by_id only) and add query helpers only when services require them.
Rationale: Avoids premature abstraction; keeps code small and easy to reason about.


## Step 5.2 - Minimal rule service

### Simplified Rule Model
Decision: Use a single Pydantic Rule class with dictionary subsections.
Rationale: Highly declarative, clearer YAML mapping, less boilerplate, and avoids unnecessary schema rigidity.

### No Nested Conditions for MVP
Decision: Only flat `conditions.all` lists are supported.
Rationale: All current business rules are expressible without nesting; avoids complexity

## Step 5.3

### Decision: Rule evaluation is triggered immediately after event persistence
Rationale: ensures all business logic related to the event occurs in a deterministic
order and maintains the pipeline integrity.

### Decision: EventProcessingService returns both event and decision
Rationale: This will be consumed in Step 5.4 for suppression and Step 5.5 for
message orchestration. It keeps the service flexible and testable.

### Decision: Continue explicit passing of `db` to repositories and RuleEvaluationService
Rationale: SQLAlchemy sessions are request-scoped. Repositories remain stateless
and session-agnostic, avoiding lifecycle and concurrency issues.

### Decision: No creation of SendRequest or Suppression rows yet
Rationale: Prevents partially implemented behavior and isolates responsibilities.
Suppression logic is handled in Step 5.4.
