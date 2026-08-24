import os
from fastapi.testclient import TestClient
from app import app
client = TestClient(app)
response = client.post('/admin/widgets', headers={'x-admin-token': os.getenv('ADMIN_TOKEN','local-demo-token'), 'x-tenant-id': 'demo'}, json={'title':'Demo signup','description':'Local demo widget','fields':['email'],'button_text':'Send'})
print(response.json())
