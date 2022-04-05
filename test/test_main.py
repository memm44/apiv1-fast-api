from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# app
import main
import database

client = TestClient(main.app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database.Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


main.app.dependency_overrides[main.get_db] = override_get_db


def test_listar_clientes_ningun_cliente_registrado():
    response = client.get('/api/v1/clientes/')
    data = response.json()
    data.clear()  # elimina clientes creados de otros tests
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0


def test_listar_clientes_uno_o_mas_clientes():
    client.post(
        "/api/v1/clientes/", json={"nombre": "miguel"},
    )
    response = client.get('/api/v1/clientes/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1


def test_crear_cliente_nuevo():
    response = client.post(
        "/api/v1/clientes/", json={"nombre": "Eduardo"},
    )
    data = response.json()
    assert response.status_code == 201
    assert isinstance(data, dict)
    assert data["nombre"] == "Eduardo"


def test_cliente_encontrado():
    # el id se va generando de uno en uno. (se crean dos clientes)
    client.post(
        "/api/v1/clientes/",
        json={"nombre": "miguel"},
    )
    client.post(
        "/api/v1/clientes/",
        json={"nombre": "anais"},
    )
    response = client.get('/api/v1/clientes/2')
    data = response.json()
    assert response.status_code == 200
    assert data["nombre"] == "anais"


def test_cliente_no_encontrado():
    response = client.get('/api/v1/clientes/4455')
    data = response.json()
    assert response.status_code == 404
    assert "detail" in data
    assert data["detail"] == "Este id de usuario no esta registrado"


def test_formato_incorrecto():
    response = client.get('/api/v1/clientes/4d')
    data = response.json()
    assert response.status_code == 422
    assert isinstance(data, dict)
    assert data["detail"][0]["msg"] == "value is not a valid integer"
    assert data["detail"][0]["type"] == "type_error.integer"


def test_crear_cuenta_usuario_registrado():
    client.post(
        "/api/v1/clientes/",
        json={"nombre": "miguel"},
    )
    response = client.post(
        "/api/v1/clientes/1/cuentas", json={"saldo_disponible": 0}
    )
    data = response.json()
    assert response.status_code == 201
    assert data["saldo_disponible"] == 0
    assert data["cliente_id"] == 1
