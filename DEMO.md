# Live Demo

## Start

Use two terminals.

Terminal 1:

```bash
source .venv/bin/activate
python seed.py
uvicorn app:app --reload --port 8000
```

Terminal 2:

```bash
python3 -m http.server 5500 --directory customer-site
```

Open `http://localhost:5500`.

## Walkthrough

1. Show the customer page on port 5500.
2. Explain that the page is on a different origin from the API.
3. Submit a valid email and show `Submission stored.`.
4. Submit the same API payload twice with the same idempotency key and show that the second response is marked as a duplicate.
5. Send a honeypot value and show the `422` response.
6. Send six rapid submissions and show the `429` rate limit response.
7. Run `pytest -q` and show the twelve passing tests.
8. State the main decision: persistence happens before the notification side effect, so a notification failure does not discard a valid lead.
9. State the main limitation: this is a local first SQLite prototype with logged notifications and in process rate limiting.

## Evaluation evidence

The README provides the setup commands, API examples, architecture, test result, and limitations. `EVIDENCE.md` maps each requirement to a named test.
