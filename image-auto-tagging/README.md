# Image Relevance and Auto-Tagging

A local-first image metadata pipeline for relevance scoring and safe auto-tagging. It accepts metadata rather than uploading personal images.

It validates records, computes a deterministic vector score, rejects low-confidence decisions, and keeps an audit-ready result. A model provider can be added later behind the same boundary.

Run:

    pip install -r image-auto-tagging/requirements.txt
    pytest -q image-auto-tagging/test_service.py

Inputs are untrusted. The service checks identifiers, vector length, candidate tags, and confidence. It stores an image identifier and decision, not the image itself.
