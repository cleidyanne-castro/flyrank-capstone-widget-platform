from fastapi.testclient import TestClient
from service import app,cosine
client=TestClient(app)
def test_scores_record():
    r=client.post('/score',json={'image_id':'img-001','vector':[0.2,0.5,0.7,0.1],'candidate_tags':['nautical','invoice','portrait']})
    assert r.status_code==200
    assert r.json()['confidence'] in {'high','review','rejected'}
def test_rejects_bad_identifier():
    r=client.post('/score',json={'image_id':'bad id','vector':[0.2,0.5,0.7],'candidate_tags':['nautical']})
    assert r.status_code==422

def test_rejects_vector_dimension_mismatch():
    try:
        cosine([1.0, 0.0], [1.0])
    except ValueError as exc:
        assert str(exc)=='vector dimensions do not match'
    else:
        raise AssertionError('dimension mismatch should fail')

def test_health():
    assert client.get('/health').json()=={'status':'ok'}
