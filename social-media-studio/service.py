import hashlib,hmac
from fastapi import FastAPI,Header,HTTPException,Request
from pydantic import BaseModel,Field
app=FastAPI(title='Social media studio',version='1.0.0')
SECRET=b'local-demo-secret'
PUBLISHED={}
class PublishRequest(BaseModel):
    idempotency_key:str=Field(min_length=8,max_length=100)
    platform:str=Field(pattern=r'^(mock|telegram|discord|mastodon)$')
    text:str=Field(min_length=1,max_length=5000)
    scheduled_for:int|None=None
def signature(payload):return hmac.new(SECRET,payload.encode(),hashlib.sha256).hexdigest()
@app.post('/v1/publish')
def publish(req:PublishRequest):
    if req.idempotency_key in PUBLISHED:
        row=PUBLISHED[req.idempotency_key]
        return {'status':'duplicate','publish_status':row['status'],**{k:v for k,v in row.items() if k!='status'}}
    if req.platform=='mock' and req.text.strip().lower()=='rate-limit':raise HTTPException(status_code=429,detail='platform rate limit',headers={'Retry-After':'30'})
    row={'idempotency_key':req.idempotency_key,'platform':req.platform,'status':'scheduled' if req.scheduled_for is not None else 'published','text_length':len(req.text),'callback_signature':signature(req.idempotency_key)}
    PUBLISHED[req.idempotency_key]=row
    return {'status':'accepted','publish_status':row['status'],**{k:v for k,v in row.items() if k!='status'}}
@app.post('/v1/callback')
async def callback(request:Request,x_signature:str|None=Header(default=None)):
    raw=await request.body();expected=hmac.new(SECRET,raw,hashlib.sha256).hexdigest()
    if not x_signature or not hmac.compare_digest(x_signature,expected):raise HTTPException(status_code=401,detail='invalid callback signature')
    return {'status':'verified'}
@app.get('/v1/status/{key}')
def status(key):
    if key not in PUBLISHED:raise HTTPException(status_code=404,detail='publish request not found')
    return PUBLISHED[key]
@app.get('/health')
def health():return {'status':'ok'}
