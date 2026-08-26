# Evidence

Run the verification command from the repository root:

```bash
pytest -q
```

Expected result:

```text
12 passed
```

## Requirement to test matrix

| Requirement | Test | Expected result |
| --- | --- | --- |
| Health endpoint | `test_health` | Returns `{"status":"ok"}` |
| Tenant isolation | `test_tenant_isolation` | A different tenant cannot list the widget |
| Cached config | `test_config_has_cache_header` | Config response includes `max-age=60` |
| Browser delivery | `test_widget_script_is_valid_javascript` | Script contains the working form and success state |
| CORS | `test_cors_preflight` | Allowed origin is returned for the customer site |
| Required fields | `test_invalid_payload` | Missing required data returns `422` |
| Honeypot | `test_honeypot` | Bot field returns `422` |
| Idempotency | `test_idempotency_returns_existing_submission` | Repeated key returns the first submission id |
| Rate limiting | `test_rate_limit` | Burst requests include a `429` response |
| Dashboard | `test_dashboard` | Tenant scoped totals are returned |
| Notification isolation | `test_notification_failure_does_not_rollback` | Stored data remains successful when the side effect fails |
| Enrichment fallback | `test_geo_provider_fallback_still_stores_submission` | Both provider failures leave empty geo fields and keep the submission |

The test suite covers the behaviors claimed in the README. It does not prove production scale, distributed rate limiting, external email delivery, or the security of a deployed environment.
