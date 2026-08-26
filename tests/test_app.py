import os
import pytest
import app as app_module
from fastapi.testclient import TestClient
from app import app, rate_buckets
client = TestClient(app)
headers = {'x-admin-token': os.getenv('ADMIN_TOKEN','local-demo-token'), 'x-tenant-id': 'tenant-a'}

@pytest.fixture
def widget():
    r = client.post('/admin/widgets', headers=headers, json={'title':'Signup','fields':['email']})
    return r.json()['id']

def test_health():
    assert client.get('/health').json() == {'status':'ok'}

def test_tenant_isolation(widget):
    other = client.get('/admin/widgets', headers={'x-admin-token':'local-demo-token','x-tenant-id':'tenant-b'})
    assert other.json() == []

def test_config_has_cache_header(widget):
    r = client.get(f'/widgets/{widget}/config')
    assert r.status_code == 200
    assert 'max-age=60' in r.headers['cache-control']

def test_widget_script_is_valid_javascript(widget):
    response = client.get('/widget.v1.js')
    assert response.status_code == 200
    assert 'Submission stored.' in response.text
    assert "type=\"email\"" in response.text

def test_cors_preflight():
    r = client.options('/submissions', headers={'Origin':'http://localhost:5500','Access-Control-Request-Method':'POST'})
    assert r.status_code == 200
    assert r.headers['access-control-allow-origin'] == 'http://localhost:5500'

def test_invalid_payload(widget):
    r = client.post('/submissions', json={'widget_id':widget,'data':{'x':'a'}})
    assert r.status_code == 422

def test_honeypot(widget):
    r = client.post('/submissions', json={'widget_id':widget,'data':{'email':'bot@example.com'},'honeypot':'spam'})
    assert r.status_code == 422

def test_idempotency_returns_existing_submission(widget):
    payload = {'widget_id':widget,'data':{'email':'same@example.com'},'idempotency_key':'fixed-key'}
    first = client.post('/submissions', json=payload)
    second = client.post('/submissions', json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()['id'] == first.json()['id']
    assert second.json()['duplicate'] is True

def test_rate_limit(widget):
    rate_buckets.clear()
    statuses = [client.post('/submissions', json={'widget_id':widget,'data':{'email':f'{i}@example.com'}}).status_code for i in range(7)]
    assert 429 in statuses

def test_dashboard(widget):
    client.post('/submissions', json={'widget_id':widget,'data':{'email':'ok@example.com'}})
    r = client.get('/dashboard/stats', headers=headers)
    assert r.status_code == 200
    assert r.json()['total'] >= 1

def test_notification_failure_does_not_rollback(widget, monkeypatch):
    monkeypatch.setenv('SIDE_EFFECT_FAIL', 'true')
    r = client.post('/submissions', json={'widget_id':widget,'data':{'email':'stored@example.com'}})
    assert r.status_code == 200
    assert r.json()['stored'] is True

def test_geo_provider_fallback_still_stores_submission(widget, monkeypatch):
    calls = []

    def failed_lookup(url, timeout):
        calls.append(url)
        raise RuntimeError('provider unavailable')

    monkeypatch.setenv('GEO_PROVIDER_A', 'https://provider-a.test/{ip}')
    monkeypatch.setenv('GEO_PROVIDER_B', 'https://provider-b.test/{ip}')
    monkeypatch.setattr(app_module.httpx, 'get', failed_lookup)
    r = client.post('/submissions', json={'widget_id':widget,'data':{'email':'geo-fallback@example.com'}})
    assert r.status_code == 200
    assert r.json()['country'] is None
    assert r.json()['city'] is None
    assert calls == ['https://provider-a.test/testclient', 'https://provider-b.test/testclient']
