# NegotiAgent

NegotiAgent is a safe purchasing-negotiation prototype. It compares deterministic vendor simulators over exactly three rounds, applies deterministic policy checks, and writes an auditable SQLite decision trail.

## Phase 1 scope

- Three local vendor simulators with transparent price floors and concessions.
- A three-round negotiation engine and offer comparison.
- Deterministic vendor, budget, and round-limit guardrails.
- SQLite audit log and a FastAPI API.
- Pytest coverage for negotiation, guardrails, trust scoring, and audit persistence.

## Phase 2: OpenAI advisor

With `OPENAI_API_KEY` set, the API calls the OpenAI Responses API to produce a short explanation of the already-determined comparison. The advisor has no tool access and cannot select vendors, change the budget, bypass policy, or execute a payment. Without a key, the API returns a safe fallback explanation.

## Run locally

Install Python 3.12+ first, then run from the project directory:

    cd backend
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn main:app --reload

Run tests from `backend` with `python -m pytest`.

Example request:

    Invoke-RestMethod -Method Post http://127.0.0.1:8000/negotiations -ContentType application/json -Body '{"item":"ergonomic chair","quantity":2,"budget":210}'

Copy `.env.example` to `.env` before enabling OpenAI or Razorpay in later phases. No real payment capability exists in this phase.
