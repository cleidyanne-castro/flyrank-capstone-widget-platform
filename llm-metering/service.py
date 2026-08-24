from datetime import datetime,timezone
from decimal import Decimal,ROUND_HALF_UP
from fastapi import FastAPI,Header,HTTPException
from pydantic import BaseModel,Field
app=FastAPI(title='LLM usage metering',version='1.0.0')
RATE_CARD={'gpt-4o-mini':(Decimal('0.00015'),Decimal('0.00060')),'claude-3-5-haiku':(Decimal('0.0008'),Decimal('0.0040'))}
TENANTS={'tenant-demo':{'api_key':'local-demo-key','quota_usd':Decimal('10.00')}}
LEDGER={}
class UsageEvent(BaseModel):
    request_id:str=Field(min_length=8,max_length=80,pattern=r'^[A-Za-z0-9_.:-]+$')
    tenant_id:str=Field(min_length=3,max_length=80)
    model:str
    input_tokens:int=Field(ge=0,le=2000000)
    output_tokens:int=Field(ge=0,le=2000000)
def price(model,ins,outs):
    if model not in RATE_CARD:raise HTTPException(status_code=422,detail='model is not on the rate card')
    ir,orr=RATE_CARD[model]
    return ((Decimal(ins)/1000*ir)+(Decimal(outs)/1000*orr)).quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP)
def auth(tenant_id,key):
    tenant=TENANTS.get(tenant_id)
    if tenant is None or key!=tenant['api_key']:raise HTTPException(status_code=401,detail='invalid tenant credentials')
    return tenant
@app.post('/v1/usage')
def ingest(event:UsageEvent,x_api_key:str|None=Header(default=None)):
    tenant=auth(event.tenant_id,x_api_key)
    if event.request_id in LEDGER:return {'status':'duplicate',**LEDGER[event.request_id]}
    cost=price(event.model,event.input_tokens,event.output_tokens)
    used=sum((r['cost'] for r in LEDGER.values() if r['tenant_id']==event.tenant_id),Decimal('0'))
    if used+cost>tenant['quota_usd']:raise HTTPException(status_code=429,detail='tenant quota exceeded')
    row={'request_id':event.request_id,'tenant_id':event.tenant_id,'model':event.model,'input_tokens':event.input_tokens,'output_tokens':event.output_tokens,'cost':cost,'recorded_at':datetime.now(timezone.utc).isoformat()}
    LEDGER[event.request_id]=row
    return {'status':'recorded',**row,'cost':str(cost)}
@app.get('/v1/tenants/{tenant_id}/summary')
def summary(tenant_id,x_api_key:str|None=Header(default=None)):
    auth(tenant_id,x_api_key)
    rows=[r for r in LEDGER.values() if r['tenant_id']==tenant_id]
    total=sum((r['cost'] for r in rows),Decimal('0'))
    models={}
    for r in rows:models[r['model']]=models.get(r['model'],0)+1
    return {'tenant_id':tenant_id,'events':len(rows),'total_cost_usd':str(total),'requests_by_model':models}
@app.get('/health')
def health():return {'status':'ok'}
