# Image Relevance and Auto-Tagging

## Scope

A local first metadata scoring boundary for image workflows. It accepts an image identifier, a numeric vector, and candidate tags. It does not upload or store personal images.

The current implementation uses a deterministic local vector function as a provider substitute. It demonstrates the API contract, validation, confidence routing, and audit-ready output. It is not a production image model.

## Reproduce

```bash
pip install -r image-auto-tagging/requirements.txt
pytest -q image-auto-tagging/test_service.py
uvicorn service:app --app-dir image-auto-tagging --reload --port 8010
```

Example request:

```bash
curl -X POST http://localhost:8010/score \
  -H 'Content-Type: application/json' \
  -d '{"image_id":"img-001","vector":[0.2,0.5,0.7,0.1],"candidate_tags":["nautical","invoice","portrait"]}'
```

The response contains the selected tag, score, confidence route, and reason.

## Evidence

The tests cover a valid score, identifier validation, vector dimension mismatch, and the health endpoint. Inputs are untrusted. The service checks identifiers, vector length, candidate tags, and confidence. It stores an image identifier and decision, not the image itself.

## Limitations

- The scorer is deterministic and does not understand raw image content.
- There is no external vector or vision provider in this repository.
- The service is local first and has no persistent result store.
- Thresholds are demonstration values and require calibration against labeled data before production use.
