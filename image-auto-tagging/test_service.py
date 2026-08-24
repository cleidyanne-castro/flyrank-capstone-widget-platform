from fastapi.testclient import TestClient
from service import app
client=TestClient(app)
def test_scores_record():
    r=client.post('/score',json={'image_id':'img-001','vector':[0.2,0.5,0.7,0.1],'candidate_tags':['nautical','invoice','portrait']})
    assert r.status_code==200
    assert r.json()['confidence'] in {'high','review','rejected'}
def test_rejects_bad_identifier():
    r=client.post('/score',json={'image_id':'bad id','vector':[0.2,0.5,0.7],'candidate_tags':['nautical']})
    assert r.status_code==422
