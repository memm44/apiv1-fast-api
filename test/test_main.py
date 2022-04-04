from fastapi.testclient import TestClient
# app
import main

client = TestClient(main.app)


def test_listar_clientes():
    response = client.get('/api/v1/clientes/')
    assert response.status_code == 200


def test_listar_cuentas():
    response = client.get('/api/v1/clientes/')
    assert response.status_code == 200


def test_cliente_encontrado():
    response = client.get('/api/v1/clientes/1')
    assert response.status_code == 200


def test_cliente_no_encontrado():
    response = client.get('/api/v1/clientes/4455')
    assert response.status_code == 404


def test_formato_incorrecto():
    response = client.get('/api/v1/clientes/4d')
    assert response.status_code == 422


