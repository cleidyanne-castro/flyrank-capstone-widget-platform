# Social Media Studio

A publishing service with one adapter boundary for Telegram, Discord, Mastodon, or a local mock. The mock keeps credentials and personal accounts out of the repository while preserving the behaviours that matter: idempotent publishing, scheduled status, rate-limit handling, and signed callbacks.

Run:

    pip install -r social-media-studio/requirements.txt
    pytest -q social-media-studio/test_service.py
