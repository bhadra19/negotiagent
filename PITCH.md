# NegotiAgent demo narrative

## Problem

Purchasing teams need fast supplier comparison without allowing an AI system to make unbounded spending decisions.

## Demo flow

1. Submit a purchase request in the web UI.
2. Watch three vendors make exactly three deterministic offers.
3. Show the policy-approved offer and the separate AI explanation.
4. Demonstrate that a changed amount or currency is rejected before Razorpay receives it.
5. Show the audit trail and a failed attempt followed by a safely idempotent retry.

## Proof points

- LLM output is explanatory only.
- Policy, trust, budgets, rounds, and payment checks are deterministic.
- Razorpay accepts Test Mode keys only.
- Batch scenarios provide a repeatable demo and regression input.
