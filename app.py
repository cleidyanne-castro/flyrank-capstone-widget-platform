import json
import os
import sqlite3
import time
import uuid
from collections import defaultdict, deque

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./widget_platform.db").replace("sqlite:///./", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "local-demo-token")
ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://localhost:8000").split(",")
app = FastAPI(title="Embeddable Widget Platform")
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=["*"], allow_headers=["*"])
limits: dict[str, deque[float]] = defaultdict(deque)
rate_buckets = limits

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript("""CREATE TABLE IF NOT EXISTS widgets(
      id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, title TEXT NOT NULL,
      description TEXT NOT NULL, fields TEXT NOT NULL, button_text TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS submissions(
      id INTEGER PRIMARY KEY AUTOINCREMENT, widget_id TEXT NOT NULL,
      tenant_id TEXT NOT NULL, payload TEXT NOT NULL, country TEXT,
      city TEXT, created_at REAL NOT NULL, idempotency_key TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS audit_events(
      id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL,
      event TEXT NOT NULL, subject_id TEXT NOT NULL, created_at REAL NOT NULL
    );""")
    return conn

class WidgetIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    fields: list[str] = Field(default_factory=lambda: ["email"], min_length=1, max_length=8)
    button_text: str = Field(default="Send", min_length=1, max_length=40)

class WidgetOut(WidgetIn):
    id: str
    tenant_id: str

class SubmissionIn(BaseModel):
    widget_id: str
    data: dict[str, str] = Field(max_length=20)
    honeypot: str = Field(default="", max_length=100)
    idempotency_key: str = Field(default="", max_length=80)

def tenant_auth(x_admin_token: str | None = Header(default=None), x_tenant_id: str | None = Header(default=None)):
    if x_admin_token != ADMIN_TOKEN or not x_tenant_id:
        raise HTTPException(401, "invalid admin credentials")
    return x_tenant_id

def get_widget(conn, widget_id: str):
    row = conn.execute("SELECT * FROM widgets WHERE id=?", (widget_id,)).fetchone()
    if not row:
        raise HTTPException(404, "widget not found")
    return row

def check_owner(row, tenant_id):
    if row["tenant_id"] != tenant_id:
        raise HTTPException(404, "widget not found")

def geo_lookup(ip: str):
    for template in (os.getenv("GEO_PROVIDER_A", ""), os.getenv("GEO_PROVIDER_B", "")):
        if not template or template.startswith("mock-down"):
            continue
        try:
            data = httpx.get(template.replace("{ip}", ip), timeout=2).json()
            return data.get("country"), data.get("city")
        except Exception:
            pass
    return None, None

def notify(submission_id: int):
    try:
        if os.getenv("SIDE_EFFECT_FAIL") == "true":
            raise RuntimeError("simulated notification failure")
        print(f"notification queued for submission {submission_id}")
    except Exception as exc:
        print(f"notification skipped for submission {submission_id}: {exc}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/admin/widgets", response_model=WidgetOut)
def create_widget(payload: WidgetIn, tenant_id: str = Depends(tenant_auth)):
    widget_id = uuid.uuid4().hex[:12]
    conn = db()
    conn.execute("INSERT INTO widgets VALUES(?,?,?,?,?,?)", (widget_id, tenant_id, payload.title, payload.description, json.dumps(payload.fields), payload.button_text))
    conn.execute("INSERT INTO audit_events(tenant_id,event,subject_id,created_at) VALUES(?,?,?,?)", (tenant_id, "widget.created", widget_id, time.time()))
    conn.commit()
    return {**payload.model_dump(), "id": widget_id, "tenant_id": tenant_id}

@app.get("/admin/widgets", response_model=list[WidgetOut])
def list_widgets(tenant_id: str = Depends(tenant_auth)):
    rows = db().execute("SELECT * FROM widgets WHERE tenant_id=?", (tenant_id,)).fetchall()
    return [{**dict(row), "fields": json.loads(row["fields"])} for row in rows]

@app.get("/admin/widgets/{widget_id}", response_model=WidgetOut)
def read_widget(widget_id: str, tenant_id: str = Depends(tenant_auth)):
    row = get_widget(db(), widget_id)
    check_owner(row, tenant_id)
    return {**dict(row), "fields": json.loads(row["fields"])}

@app.put("/admin/widgets/{widget_id}", response_model=WidgetOut)
def update_widget(widget_id: str, payload: WidgetIn, tenant_id: str = Depends(tenant_auth)):
    conn = db()
    row = get_widget(conn, widget_id)
    check_owner(row, tenant_id)
    conn.execute("UPDATE widgets SET title=?,description=?,fields=?,button_text=? WHERE id=?", (payload.title, payload.description, json.dumps(payload.fields), payload.button_text, widget_id))
    conn.execute("INSERT INTO audit_events(tenant_id,event,subject_id,created_at) VALUES(?,?,?,?)", (tenant_id, "widget.updated", widget_id, time.time()))
    conn.commit()
    return {**payload.model_dump(), "id": widget_id, "tenant_id": tenant_id}

@app.delete("/admin/widgets/{widget_id}", status_code=204)
def delete_widget(widget_id: str, tenant_id: str = Depends(tenant_auth)):
    conn = db()
    row = get_widget(conn, widget_id)
    check_owner(row, tenant_id)
    conn.execute("DELETE FROM submissions WHERE widget_id=?", (widget_id,))
    conn.execute("DELETE FROM widgets WHERE id=?", (widget_id,))
    conn.commit()
    return Response(status_code=204)

@app.get("/widgets/{widget_id}/config")
def widget_config(widget_id: str, response: Response):
    row = get_widget(db(), widget_id)
    response.headers["Cache-Control"] = "public, max-age=60"
    return {"id": row["id"], "title": row["title"], "description": row["description"], "fields": json.loads(row["fields"]), "button_text": row["button_text"]}

@app.get("/widget.v1.js")
def widget_script():
    script = "(function(){const s=document.currentScript,id=new URL(s.src).searchParams.get('id');fetch('/widgets/'+id+'/config').then(r=>r.json()).then(c=>{const root=document.createElement('div');root.innerHTML='<h3>'+c.title+'</h3><p>'+c.description+'</p><form><input name=&quot;email&quot; type='email' required><input name=&quot;website&quot; tabindex='-1' autocomplete='off' style='display:none'><button>'+c.button_text+'</button></form>';s.after(root);root.querySelector('form').onsubmit=async e=>{e.preventDefault();const data=Object.fromEntries(new FormData(e.target));await fetch('/submissions',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({widget_id:id,data,honeypot:data.website,idempotency_key:crypto.randomUUID()})});};});})();"
    return Response(script, media_type="application/javascript", headers={"Cache-Control": "public, max-age=31536000, immutable"})

@app.options("/submissions")
def submission_preflight():
    return Response(status_code=204)

@app.post("/submissions")
def submit(payload: SubmissionIn, request: Request, background_tasks: BackgroundTasks):
    conn = db()
    row = get_widget(conn, payload.widget_id)
    raw = json.dumps(payload.model_dump())
    required = json.loads(row["fields"])
    if any(not payload.data.get(field) for field in required):
        raise HTTPException(422, "required field missing")
    if len(raw) > 6000:
        raise HTTPException(413, "payload too large")
    if payload.honeypot:
        raise HTTPException(422, "spam rejected")
    if payload.idempotency_key:
        previous = conn.execute("SELECT id FROM submissions WHERE idempotency_key=?", (payload.idempotency_key,)).fetchone()
        if previous:
            return {"id": previous["id"], "stored": True, "duplicate": True}
    ip = request.client.host if request.client else "unknown"
    bucket = limits[f"{ip}:{payload.widget_id}"]
    now = time.time()
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= 5:
        raise HTTPException(429, "rate limit exceeded")
    bucket.append(now)
    country, city = geo_lookup(ip)
    cur = conn.execute("INSERT INTO submissions(widget_id,tenant_id,payload,country,city,created_at,idempotency_key) VALUES(?,?,?,?,?,?,?)", (payload.widget_id, row["tenant_id"], json.dumps(payload.data), country, city, now, payload.idempotency_key or None))
    conn.execute("INSERT INTO audit_events(tenant_id,event,subject_id,created_at) VALUES(?,?,?,?)", (row["tenant_id"], "submission.accepted", str(cur.lastrowid), now))
    conn.commit()
    background_tasks.add_task(notify, cur.lastrowid)
    return {"id": cur.lastrowid, "stored": True, "country": country, "city": city}

@app.get("/dashboard/stats")
def stats(tenant_id: str = Depends(tenant_auth)):
    conn = db()
    total = conn.execute("SELECT COUNT(*) c FROM submissions WHERE tenant_id=?", (tenant_id,)).fetchone()["c"]
    by_widget = conn.execute("SELECT widget_id, COUNT(*) c FROM submissions WHERE tenant_id=? GROUP BY widget_id", (tenant_id,)).fetchall()
    by_country = conn.execute("SELECT country, COUNT(*) c FROM submissions WHERE tenant_id=? GROUP BY country", (tenant_id,)).fetchall()
    return {"total": total, "by_widget": {r["widget_id"]: r["c"] for r in by_widget}, "by_country": {r["country"] or "unknown": r["c"] for r in by_country}}
