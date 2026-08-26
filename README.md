# FlyRank Capstone Widget Platform

## What it does

This capstone provides an embeddable lead capture widget and a tenant scoped API. A customer site loads one script tag. The script fetches widget configuration from the API, renders a form, submits validated data, and displays success or failure feedback.

The API stores submissions in SQLite and exposes tenant scoped dashboard totals. The public path applies CORS, validation, payload limits, a honeypot, per IP and widget rate limiting, idempotency, optional geo enrichment, and a background notification side effect.

## Repository scope

The root files are the capstone implementation. The other top level directories are earlier portfolio exercises retained in this repository. Reviewers can focus on `app.py`, `seed.py`, `customer-site/`, `tests/`, and the root documentation files.

## Requirements

- Python 3.11 or later
- pip

## Reproduce the demo

Use two terminals from the repository root.

Terminal 1:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
uvicorn app:app --reload --port 8000
```

Terminal 2:

```bash
python3 -m http.server 5500 --directory customer-site
```

Open `http://localhost:5500`. The page loads the widget from the API on port 8000. Submit a valid email and verify the success message. A browser developer console can show the cross origin requests and the API response.

## API checks

The seeded widget id is `demo` and the seeded tenant id is `demo`.

```bash
curl http://localhost:8000/health
curl http://localhost:8000/widgets/demo/config
curl -i http://localhost:8000/widget.v1.js?id=demo
curl -X POST http://localhost:8000/submissions \
  -H 'Content-Type: application/json' \
  -d '{"widget_id":"demo","data":{"email":"reviewer@example.com"},"idempotency_key":"review-001"}'
curl -H 'x-admin-token: local-demo-token' \
  -H 'x-tenant-id: demo' \
  http://localhost:8000/dashboard/stats
```

Expected behavior includes a successful stored response, a duplicate response when the same idempotency key is sent again, `422` for a honeypot value, `429` after the burst limit, and tenant scoped dashboard results.

## Test and evaluation

```bash
pytest -q
```

The test suite has twelve tests covering health, tenant isolation, cached config, widget script content, CORS preflight, validation, honeypot rejection, idempotency, rate limiting, dashboard output, notification failure isolation, and geo provider fallback.

The full requirement to test matrix is in `EVIDENCE.md`. The live walkthrough is in `DEMO.md`.

## Architecture

```text
customer site
  -> versioned widget script
  -> cached widget config
  -> CORS submission endpoint
  -> validation and abuse checks
  -> optional enrichment
  -> SQLite persistence
  -> tenant scoped dashboard aggregates
```

## Security and data decisions

- Admin routes require an admin token and tenant id.
- Widget ownership is checked before admin reads, updates, or deletes.
- Public input is validated before persistence.
- A honeypot and a per IP and widget burst limit reduce simple abuse.
- Idempotency keys prevent duplicate storage for retried submissions.
- Geo enrichment is non critical and falls back to empty values.
- Notification failures occur after persistence and do not remove a valid submission.

## Limitations

- This is a local first prototype using SQLite.
- The demo notification is logged and is not an email delivery integration.
- The widget uses a local API URL and is not a deployed public service.
- Rate limiting is in process and is not shared across multiple workers.
- The repository retains earlier exercises at the top level, so the capstone scope must be read from the root files listed above.

## AI usage

AI tools supported drafting and review of parts of the implementation and documentation. The code, tests, links, and final validation were checked against the repository contents.
