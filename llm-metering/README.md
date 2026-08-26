# LLM Usage Metering and Billing Service

## Scope

A small usage ledger for multi-tenant AI applications. Each request is recorded once, priced from a versioned rate card, and aggregated into a tenant summary.

Included: tenant-scoped API keys, idempotent ingestion, token and cost calculation, quota checks, summaries, and a storage boundary that can be replaced by SQLite. Raw prompts and completions are not stored.

## Reproduce

```bash
pip install -r llm-metering/requirements.txt
pytest -q llm-metering/test_service.py
uvicorn service:app --app-dir llm-metering --reload --port 8020
```

Example request:

```bash
curl -X POST http://localhost:8020/v1/usage \
  -H 'x-api-key: local-demo-key' \
  -H 'Content-Type: application/json' \
  -d '{"request_id":"request-001","tenant_id":"tenant-demo","model":"gpt-4o-mini","input_tokens":1000,"output_tokens":500}'
curl -H 'x-api-key: local-demo-key' http://localhost:8020/v1/tenants/tenant-demo/summary
```

The first request is recorded. Repeating the same `request_id` returns a duplicate response without adding another ledger row.

## Evidence

The tests cover idempotent ingestion, invalid credentials, unknown models, quota enforcement, and the health endpoint.

## Limitations

- The ledger is in memory and resets when the process restarts.
- The demo API key is hardcoded for local testing and is not a production credential.
- The summary is cumulative for the process and has no calendar month filter.
- Quota calculation is not protected by a database transaction or distributed lock.
- Production use requires a secrets manager, durable transactional storage, and concurrency controls.
