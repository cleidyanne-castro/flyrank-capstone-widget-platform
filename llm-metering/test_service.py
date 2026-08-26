from fastapi.testclient import TestClient
from service import app,LEDGER
client=TestClient(app)
def setup_function():LEDGER.clear()
def body(key='request-001'):return {'request_id':key,'tenant_id':'tenant-demo','model':'gpt-4o-mini','input_tokens':1000,'output_tokens':500}
def test_idempotent_usage():
    h={'x-api-key':'local-demo-key'}
    assert client.post('/v1/usage',json=body(),headers=h).json()['status']=='recorded'
    assert client.post('/v1/usage',json=body(),headers=h).json()['status']=='duplicate'
    assert client.get('/v1/tenants/tenant-demo/summary',headers=h).json()['events']==1
def test_wrong_key():assert client.post('/v1/usage',json=body(),headers={'x-api-key':'wrong'}).status_code==401
def test_unknown_model():
    p=body('request-002');p['model']='unknown'
    assert client.post('/v1/usage',json=p,headers={'x-api-key':'local-demo-key'}).status_code==422

def test_quota_is_enforced():
    p=body('request-003');p['model']='claude-3-5-haiku';p['input_tokens']=2000000;p['output_tokens']=2000000
    assert client.post('/v1/usage',json=p,headers={'x-api-key':'local-demo-key'}).status_code==200
    p['request_id']='request-004'
    assert client.post('/v1/usage',json=p,headers={'x-api-key':'local-demo-key'}).status_code==429

def test_health():
    assert client.get('/health').json()=={'status':'ok'}
