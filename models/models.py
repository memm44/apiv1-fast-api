import datetime
from database import Base
from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    cuentas = relationship("Cuenta", back_populates="cliente")


class Cuenta(Base):
    __tablename__ = "cuentas"
    id = Column(Integer, primary_key=True, index=True)
    saldo_disponible = Column(Float, default=0.0)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    cliente = relationship("Cliente", back_populates="cuentas")
    movimientos = relationship("Movimiento", back_populates="cuenta")


class Movimiento(Base):
    __tablename__ = "movimientos"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, unique=False, index=True, default=datetime.datetime.utcnow())
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"))
    cuenta = relationship("Cuenta", back_populates="movimientos")
    movimiento_detalles = relationship("MovimientoDetalle", cascade="all,delete", backref="parent")


class MovimientoDetalle(Base):
    __tablename__ = "movimiento_detalles"
    id = Column(Integer, primary_key=True, index=True)
    movimiento_id = Column(Integer, ForeignKey("movimientos.id"))
    tipo = Column(String, unique=False, index=False)
    importe = Column(Float)
    movimiento = relationship("Movimiento", back_populates="movimiento_detalles", overlaps="parent")

