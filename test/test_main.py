from fastapi.testclient import TestClient
# app
import main

client = TestClient(main.app)


def test_leer_clientes():
    response = client.get('/clientes/')

    assert response.status_code == 200

