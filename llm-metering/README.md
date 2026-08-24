# LLM Usage Metering and Billing Service

A small usage ledger for multi-tenant AI applications. Each request is recorded once, priced from a versioned rate card, and aggregated into a billing summary.

Included: tenant-scoped API keys, idempotent ingestion, token and cost calculation, quota checks, monthly summaries, and SQLite-ready data structures. Raw prompts and completions are not stored.

Run:

    pip install -r llm-metering/requirements.txt
    pytest -q llm-metering/test_service.py

Production use would replace the local key store with a secrets manager and a transactional database.
