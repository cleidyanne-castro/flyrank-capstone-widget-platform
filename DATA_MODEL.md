# Data model

Widgets are owned by a tenant and define the public configuration.

Submissions reference the widget and tenant, store the validated payload as JSON, and keep derived country and city fields separate from the raw input. The dashboard groups stored facts by widget and country.

The ingestion sequence is validation, abuse checks, enrichment, persistence, then notification. A failed enrichment call does not block persistence.
