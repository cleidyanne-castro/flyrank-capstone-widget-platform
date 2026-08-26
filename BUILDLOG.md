# Build log

The implementation was reviewed as a local first FastAPI service with a separate customer page. The data model keeps widgets, submissions, and audit events separate. The submission path validates input, applies abuse checks, enriches when configured, persists the result, and then runs the notification side effect.

The first public review identified two issues. The widget script had invalid JavaScript quoting in the form markup, and the evidence file listed behaviors that were not covered by tests. The script now renders valid markup with success and failure states. The suite now contains twelve tests and `EVIDENCE.md` maps every claimed behavior to a named test.

The core runs locally with SQLite. Geo providers are optional during tests and both provider failures result in a stored submission with empty geo fields. Notifications are logged rather than delivered by email. No API key is included.

AI tools supported drafting and review of parts of the implementation. The code and final test results were checked against the repository contents.
