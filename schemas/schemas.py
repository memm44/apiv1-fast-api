import datetime
from typing import List, Optional
from pydantic import BaseModel


class MovimientoBase(BaseModel):
    fecha: Optional[datetime.datetime]


class Movimiento(MovimientoBase):
    id = int
    cuenta_id = int

    class Config:
        orm_mode = True


class MovimientoDetalleBase(BaseModel):
    tipo: str
    importe: float



class MovimientoDetalle(MovimientoDetalleBase):
    movimiento_id = int


class CuentaBase(BaseModel):
    saldo_disponible: Optional[float]


class Cuenta(CuentaBase):
    id: int
    cliente_id: int
    movimientos: List[Movimiento] = []

    class Config:
        orm_mode = True


class ClienteBase(BaseModel):
    nombre: str


class Cliente(ClienteBase):
    id: int
    cuentas: List[Cuenta] = []

    class Config:
        orm_mode = True


class ClientRegister(ClienteBase):
    pass


class CuentaRegister(CuentaBase):
    pass


class MovimientoRegister(MovimientoBase):
    pass


class MovimientoDetalleRegister(MovimientoDetalleBase):
    pass
