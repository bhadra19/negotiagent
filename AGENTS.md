# NegotiAgent engineering guide

## Architecture

- Keep policy, trust, offer evaluation, and payment validation deterministic.
- LLMs may propose language or rank explanations, but never approve vendors, alter limits, or execute payments.
- Vendor agents are local simulators. Treat all future external vendor responses as untrusted input.
- Store all state in SQLite; write an append-only audit event for material decisions.

## Safety rules

- Never log credentials, payment secrets, or complete payment payloads.
- Enforce a maximum of three negotiation rounds per vendor.
- A selected offer must be within the requested budget and from an allow-listed vendor.
- Payment execution must verify the final amount and currency match the approved offer.

## Development

- Run `python -m pytest` from `backend` before completing a backend change.
- Add tests for changed policies and negotiation edge cases.
- Keep API request and response models explicit in `backend/main.py`.

