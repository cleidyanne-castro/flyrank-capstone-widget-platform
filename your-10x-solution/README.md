# My 10x Solution - Cleidyanne Castro Pereira

## Problem

Small teams often receive operational requests through public forms and lose context between intake, validation, enrichment, and follow-up. The result is noisy data and weak visibility into what happened.

## Proposed solution

The Embeddable Widget and Lead-Capture Platform addresses that problem with tenant scoped intake, validation, CORS, rate limiting, idempotency, optional geo enrichment, audit events, background notifications, and dashboard totals.

The user flow is:

1. A tenant creates a widget with required fields.
2. A customer page loads the widget configuration from a separate origin.
3. A visitor submits a lead.
4. The API validates, limits, enriches, stores, and audits the lead.
5. The tenant reads aggregate results from the dashboard endpoint.

## Program concepts and success criteria

Five program concepts are represented: API endpoints, a database, authentication, background work, and reporting. Caching is included as an additional control.

Success is measured by accepted valid input, rejected invalid or abusive input, duplicate protection, tenant scoped dashboard totals, and persistence when optional dependencies fail.

This is a practical bridge between data engineering and cybersecurity. The pipeline handles untrusted input while treating enrichment and notifications as optional dependencies.

## Evidence and limits

The implementation lives in the root capstone files in the public repository. This directory is the solution brief, not a second implementation.

Repository: https://github.com/cleidyanne-castro/flyrank-capstone-widget-platform

The prototype is local first, uses SQLite, logs notifications instead of delivering email, and uses in process rate limiting. It is not presented as a production deployment.
