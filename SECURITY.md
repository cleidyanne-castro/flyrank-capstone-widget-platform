# Security notes

The public submission endpoint is the trust boundary.

- Admin routes require a token and tenant id.
- Payloads are validated before business logic.
- A honeypot catches simple bots.
- A per-IP and per-widget bucket returns 429 after a burst.
- The API never logs tokens or raw secrets.
- Geo enrichment is non-critical and can fail closed.
- The notification side effect runs after storage and cannot make a valid submission disappear.
- SQLite is local demo storage. Production deployment would add a real secret manager, durable rate limiting, structured audit logs, and HTTPS termination.
