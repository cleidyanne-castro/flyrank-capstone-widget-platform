# FlyRank Capstone Widget Platform

A local embeddable widget and lead-capture API. A customer creates a widget, pastes one script tag into a second-origin HTML page, and receives validated, rate-limited submissions in a tenant-scoped dashboard.

## Architecture

    owner -> authenticated widget API -> SQLite
    customer page -> cached widget config and versioned script
    visitor -> CORS submission API -> validation -> abuse checks -> geo fallback -> storage -> background notification
    owner -> dashboard stats API

## Run

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python seed.py
    uvicorn app:app --reload

Serve customer-site from another origin:

    python3 -m http.server 5500 --directory customer-site

Open http://localhost:5500.

## API

Admin endpoints require x-admin-token and x-tenant-id headers. The public endpoints are /widgets/{id}/config, /widget.v1.js, and /submissions. Dashboard stats are available at /dashboard/stats for the authenticated tenant.

## Tests

    pytest -q

The tests cover tenant isolation, cached config, CORS preflight, invalid input, honeypot rejection, rate limiting, and dashboard output.

## Limitations

This version is local-first and uses SQLite. Geo calls are optional and the fallback result is empty when providers are unavailable. The notification side effect is logged rather than delivered by email. The public widget script uses a local API URL for the demo.
