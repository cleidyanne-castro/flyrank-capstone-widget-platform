# Evidence

- Widget management: test_tenant_isolation verifies tenant-scoped reads.
- Widget delivery: test_config_has_cache_header verifies cached config delivery.
- Public submission API: test_invalid_payload verifies clean validation errors.
- Abuse protection: test_honeypot and test_rate_limit verify spam rejection and 429 responses.
- Enrichment fallback: geo_lookup tries provider A, then provider B, then stores without geo when both fail.
- Safe side effect: send_side_effect runs as a background task.
- Dashboard: test_dashboard verifies aggregate statistics.
- CORS: test_cors_preflight verifies OPTIONS handling.
