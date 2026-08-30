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

## Phase 3: policy, trust, and substitution

Every selected offer must come from an approved vendor, satisfy the budget and three-round limit, and meet the minimum deterministic trust score. `POST /substitutions` returns only catalogued alternatives that fit the submitted quantity and budget; it never invents an alternative.

## Phase 4: Razorpay Test Mode

`POST /payments/orders` creates a Razorpay Test Mode order only after loading the approved offer saved by the negotiation. It verifies that the submitted amount and currency exactly match the approved offer before it calls Razorpay, then sends the amount in paise. Use only `rzp_test_` credentials in `.env`; live keys are rejected by this prototype.

## Phase 5: audit and retries

Every payment request requires an idempotency key. Repeating a successful key replays the original order response without creating another provider order. Failed attempts are recorded with a safe failure category; retry with a new idempotency key to create the next auditable attempt. `GET /negotiations/{negotiation_id}/payment-attempts` returns the ordered retry history.

## Run locally

Install Python 3.12+ first, then run from the project directory:

    cd backend
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn main:app --reload

Run tests from `backend` with `python -m pytest`.

Run the React demo from `frontend` with `npm install` followed by `npm run dev`. It expects the API at `http://127.0.0.1:8000`; set `VITE_API_BASE_URL` to override it.

For a containerized demo, copy `.env.example` to `.env` and run `docker compose up --build`.

Example request:

    Invoke-RestMethod -Method Post http://127.0.0.1:8000/negotiations -ContentType application/json -Body '{"item":"ergonomic chair","quantity":2,"budget":210}'

Copy `.env.example` to `.env` before enabling OpenAI or Razorpay. Razorpay is limited to Test Mode in this prototype.

## Phase 6: demo and batch evaluation

The React/Vite demo UI shows negotiation offers, the policy decision, AI explanation, and Test Mode order creation. `demo-data/batch-scenarios.json` is a repeatable payload for `POST /batch/negotiations`; batch evaluation intentionally does not invoke the LLM or payment provider.
