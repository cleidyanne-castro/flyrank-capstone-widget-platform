# FlyRank Capstone Widget Platform

A local embeddable widget and lead-capture API built around two concerns from my portfolio: protecting untrusted public input and turning submissions into usable data.

The system lets a tenant create a widget, give a customer one script tag, and collect validated submissions from a different origin. The public path includes CORS, payload validation, a honeypot, per-widget rate limiting, optional geo enrichment, SQLite persistence, and a background notification task. The dashboard endpoint exposes counts by widget.

## Architecture

    owner -> authenticated widget API -> SQLite
    customer page -> cached widget config and versioned script
    visitor -> CORS submission API -> validation -> abuse checks -> geo lookup -> storage
    owner -> tenant-scoped dashboard stats

## Security angle

The client is treated as hostile. Admin routes require a token and tenant header. Public submissions are size-limited, validated before storage, protected by a honeypot and rate limit, and stored with the widget tenant. Secrets are environment variables only. The local side effect can fail without changing the stored result.

## Data engineering angle

The submission path is an ingestion pipeline: validate, normalize, enrich, persist, and aggregate. The schema keeps widget ownership and submission facts separate, while the dashboard query provides a small analytical view by widget. The geo provider is optional and can degrade to an unknown value.

## Run

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python seed.py
    uvicorn app:app --reload

Serve customer-site from another origin:

    python3 -m http.server 5500 --directory customer-site

Open http://localhost:5500.

## Tests

    pytest -q

The tests cover tenant isolation, cached config, CORS preflight, invalid input, honeypot rejection, rate limiting, and dashboard output.

## Limitations

This version is local-first and uses SQLite. Geo calls are optional and the fallback result is empty when providers are unavailable. The notification side effect is logged rather than delivered by email. The public widget script uses a local API URL for the demo.
