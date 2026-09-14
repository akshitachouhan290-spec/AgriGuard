import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health():
    r=client.get('/'); assert r.status_code==200; assert r.json()['status']=='ok'
def test_core_endpoints():
    assert client.get('/farmers/1').status_code==200
    assert client.get('/fields/farmer/1').status_code==200
    assert client.get('/crops/').status_code==200
    assert client.get('/api/weather').status_code==200
    assert client.get('/analyze/history/1').status_code==200
