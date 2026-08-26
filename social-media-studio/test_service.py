import hashlib,hmac,json
from fastapi.testclient import TestClient
from service import app,PUBLISHED,SECRET
client=TestClient(app)
def setup_function():PUBLISHED.clear()
def test_idempotent_publish():
    p={'idempotency_key':'post-0001','platform':'mock','text':'data quality update'}
    assert client.post('/v1/publish',json=p).json()['status']=='accepted'
    assert client.post('/v1/publish',json=p).json()['status']=='duplicate'
def test_rate_limit():
    r=client.post('/v1/publish',json={'idempotency_key':'post-0002','platform':'mock','text':'rate-limit'})
    assert r.status_code==429 and r.headers['retry-after']=='30'
def test_signed_callback():
    raw=json.dumps({'key':'post-0001'}).encode();sig=hmac.new(SECRET,raw,hashlib.sha256).hexdigest()
    assert client.post('/v1/callback',content=raw,headers={'x-signature':sig}).json()=={'status':'verified'}
    assert client.post('/v1/callback',content=raw,headers={'x-signature':'bad'}).status_code==401

def test_scheduled_status():
    p={'idempotency_key':'post-0003','platform':'mock','text':'scheduled update','scheduled_for':0}
    r=client.post('/v1/publish',json=p)
    assert r.status_code==200
    assert r.json()['status']=='accepted'
    assert client.get('/v1/status/post-0003').json()['status']=='scheduled'

def test_health():
    assert client.get('/health').json()=={'status':'ok'}
