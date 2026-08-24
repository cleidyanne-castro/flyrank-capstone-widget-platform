# Evidence

The local verification command is:

    pytest -q

Result:

    8 passed

Coverage:

- Widget management: tenant-scoped reads are checked.
- Widget delivery: config includes a cache header.
- Public submission API: missing required fields return 422.
- Abuse protection: honeypot rejection and burst rate limiting return 4xx responses.
- CORS: preflight returns the allowed origin header.
- Idempotency: repeated keys return the stored submission id.
- Enrichment: provider A is attempted before provider B, then the record is stored without geo if both fail.
- Safe side effect: notification failures are caught after persistence.
- Dashboard: totals and country aggregates are returned per tenant.
