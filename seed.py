import json
import os
import sqlite3
from app import DB_PATH

conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS widgets(id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, fields TEXT NOT NULL, button_text TEXT NOT NULL)")
conn.execute("INSERT OR REPLACE INTO widgets VALUES(?,?,?,?,?,?)", ("demo", "demo", "Demo signup", "A local demo widget", json.dumps(["email"]), "Send"))
conn.commit()
print({"widget_id": "demo", "tenant_id": "demo"})
