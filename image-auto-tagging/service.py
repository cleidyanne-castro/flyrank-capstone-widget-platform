from math import sqrt
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
app=FastAPI(title='Image relevance service',version='1.0.0')
class ImageRecord(BaseModel):
    image_id:str=Field(min_length=1,max_length=120,pattern=r'^[A-Za-z0-9_.:-]+$')
    vector:list[float]=Field(min_length=3,max_length=512)
    candidate_tags:list[str]=Field(min_length=1,max_length=20)
class TagDecision(BaseModel):
    image_id:str
    tag:str
    score:float
    confidence:Literal['high','review','rejected']
    reason:str
def cosine(a,b):
    if len(a)!=len(b): raise ValueError('vector dimensions do not match')
    d=sqrt(sum(x*x for x in a)*sum(y*y for y in b))
    return 0.0 if d==0 else sum(x*y for x,y in zip(a,b))/d
def tag_vector(tag,size):
    seed=sum(ord(c) for c in tag)
    return [((seed+i*17)%101)/100 for i in range(size)]
def decide(record):
    scored=[(tag,cosine(record.vector,tag_vector(tag,len(record.vector)))) for tag in record.candidate_tags]
    tag,score=max(scored,key=lambda x:x[1])
    if score<0.45: level,reason='rejected','score below automatic tagging threshold'
    elif score<0.70: level,reason='review','score requires a human review'
    else: level,reason='high','score passed the automatic tagging threshold'
    return TagDecision(image_id=record.image_id,tag=tag,score=round(score,4),confidence=level,reason=reason)
@app.post('/score',response_model=TagDecision)
def score_image(record:ImageRecord):
    try:return decide(record)
    except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
@app.get('/health')
def health():return {'status':'ok'}
