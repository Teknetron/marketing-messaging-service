## Properties options per event type
```json
{
  "signup_completed": {
    "user_id": "Unique identifier for registered user",
    "timestamp": "Time of signup completion",
    "signup_method": "Authentication provider used",
    "subscription_type": "Selected user subscription tier"
  },
  "link_bank_success": {
    "bank_name": "Name of linked financial institution",
    "verification_method": "Method used to verify account",
    "is_first_bank": "Indicates first bank connection milestone"
  },
  "payment_initiated": {
    "amount": "Total value being transferred",
    "currency": "Three-letter ISO currency code",
    "payment_method": "Type of transaction category",
    "recipient_name": "Name of fund recipient"
  },
  "payment_failed": {
    "amount": "Value of rejected transaction",
    "failure_reason": "Determines specific recovery instructions",
    "attempt_number": "Tracks retry frequency for escalation",
    "error_code": "Internal technical error mapping"
  }
}
```

A rule is:

- Triggered by an event type

- Filtered by conditions (user_traits + event.properties + other context)

- Produces a decision:

  - send template X via channel Y

  - or suppress it (dedup / opt-out / cooldown)

- Produces an explanation (why matched / why suppressed)