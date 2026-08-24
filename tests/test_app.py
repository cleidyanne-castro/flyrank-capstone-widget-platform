import os
import pytest
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

def test_cors_preflight():
    r = client.options('/submissions', headers={'Origin':'http://localhost:5500','Access-Control-Request-Method':'POST'})
    assert r.status_code == 204

def test_invalid_payload(widget):
    r = client.post('/submissions', json={'widget_id':widget,'data':{'x':'a'}})
    assert r.status_code == 422

def test_honeypot(widget):
    r = client.post('/submissions', json={'widget_id':widget,'data':{'email':'bot@example.com'},'honeypot':'spam'})
    assert r.status_code == 422

def test_rate_limit(widget):
    rate_buckets.clear()
    statuses = [client.post('/submissions', json={'widget_id':widget,'data':{'email':f'{i}@example.com'}}).status_code for i in range(7)]
    assert 429 in statuses

def test_dashboard(widget):
    client.post('/submissions', json={'widget_id':widget,'data':{'email':'ok@example.com'}})
    r = client.get('/dashboard/stats', headers=headers)
    assert r.status_code == 200
    assert r.json()['total'] >= 1
