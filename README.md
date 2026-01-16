# Project Structure: marketing-messaging-service

```
marketing-messaging-service/
├── .env
├── .gitignore
├── pyproject.toml
├── README.md
└── src/
    └── marketing_messaging_service/
        ├── __init__.py
        ├── main.py                     # Entry point
        │
        ├── config/                     # Configuration & Rules
        │   ├── __init__.py
        │   ├── rules.yaml
        │   └── settings.py
        │
        ├── controllers/                # API & Event Entry Points
        │   ├── __init__.py
        │   ├── audit_controller.py
        │   └── event_controller.py
        │
        ├── services/                   # Business Logic Layer
        │   ├── __init__.py
        │   ├── audit_service.py
        │   ├── deduplication_service.py
        │   ├── event_processing_service.py
        │   └── rule_evaluation_service.py
        │
        ├── repositories/               # Data Access Layer
        │   ├── __init__.py
        │   ├── event_repository.py
        │   ├── interfaces.py
        │   ├── send_request_repository.py
        │   └── suppression_repository.py
        │
        ├── models/                     # Domain Entities
        │   ├── __init__.py
        │   ├── event.py
        │   ├── event_properties.py
        │   ├── send_request.py
        │   ├── suppression.py
        │   └── user_traits.py
        │
        └── infrastructure/             # External Integrations
            ├── __init__.py
            ├── database.py
            └── iterable_stub.py
```