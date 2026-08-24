# Build log

AI helped draft the first FastAPI structure and test cases. I reviewed the code, simplified the data model, added the tenant boundary, and kept provider and side-effect failures explicit. No API key was added.

The core runs locally with SQLite. The capstone brief allows a local customer page and no hosting. Geo providers are optional during tests and the fallback result is deterministic when they are unavailable.
