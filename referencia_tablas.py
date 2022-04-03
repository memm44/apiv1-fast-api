# pydantic
from pydantic import BaseModel


class Cuenta(BaseModel):
    cliente: str
    saldo_disponible: str

    def get_total_usd(self):
        # https://www.dolarsi.com/api/api.php?type=valoresprincipales,
        pass


class Movimiento(BaseModel):
    id: int
    fecha: str
    cliente: str


class MovimientoDetalle(BaseModel):
    movimiento: str
    tipo: str
    detalle: str

    def get_total_actual(self):
        pass


def editar_cliente():
    pass


def eliminar_cliente():
    pass


def consultar_cliente():
    pass


def listar_clientes():
    pass


def registrar_movimiento():
    pass


def eleiminar_movimiento():
    pass


def consultar_movimiento():
    pass
