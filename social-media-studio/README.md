# Social Media Studio

## Scope

A publishing service with one adapter boundary for Telegram, Discord, Mastodon, or a local mock. The repository implements the local mock and the API contract. It does not publish to real social platforms.

The mock preserves the behaviors that matter for review: idempotent publishing, scheduled status, rate-limit handling, and signed callbacks. Credentials and personal accounts stay out of the repository.

## Reproduce

```bash
pip install -r social-media-studio/requirements.txt
pytest -q social-media-studio/test_service.py
uvicorn service:app --app-dir social-media-studio --reload --port 8030
```

Example request:

```bash
curl -X POST http://localhost:8030/v1/publish \
  -H 'Content-Type: application/json' \
  -d '{"idempotency_key":"post-0001","platform":"mock","text":"data quality update"}'
curl http://localhost:8030/v1/status/post-0001
```

## Evidence

The tests cover idempotent publishing, retry metadata for a simulated rate limit, scheduled status, signed callback verification, and health.

## Limitations

- The current adapter is a mock and no external post is sent.
- Scheduling stores a status but has no worker or durable queue.
- The signing secret is a local demo value and must come from a secret manager in production.
- Publication state is held in memory and resets on restart.
