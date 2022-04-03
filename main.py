# python
# !/usr/bin/env python3
from typing import List

# pydantic
from pydantic import BaseModel

# sqlalchemy
from sqlalchemy.orm import Session

# fastapi
from fastapi import Depends, FastAPI, HTTPException

from database import SessionLocal, engine
from models import models
from schemas import schemas

from operations import op_monetarias

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"Hello": "world"}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/clientes/", response_model=schemas.Cliente)
def crear_cliente(cliente: schemas.ClientRegister, db: Session = Depends(get_db)):
    db_user = op_monetarias.obtener_cliente_por_nombre(db, cliente.nombre)
    if db_user:
        raise HTTPException(status_code=400, detail="este nombre de cliente ya esta registrado")
    return op_monetarias.crear_cliente(db=db, cliente=cliente)


@app.get("/clientes/", response_model=List[schemas.Cliente])
def listar_todos_los_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = op_monetarias.listar_clientes(db, skip=skip, limit=limit)
    return users


@app.get("/clientes/{user_id}", response_model=schemas.Cliente)
def obtener_cliente_por_id(user_id: int, db: Session = Depends(get_db)):
    db_user = op_monetarias.obtener_cliente_por_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Este id de usuario no esta registrado")
    return db_user


@app.delete("/clientes/{user_id}", response_model=schemas.Cliente)
def eliminar_cliente_por_id(user_id: int, db: Session = Depends(get_db)):
    db_user_deleted = op_monetarias.eliminar_cliente_por_id(db, user_id)
    if db_user_deleted is False:
        raise HTTPException(status_code=404, detail="Este id de usuario no esta registrado")
    return {"ok": True}


@app.get("/cuentas/")
def listar_cuentas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cuentas = op_monetarias.listar_cuentas(db, skip=skip, limit=limit)
    return cuentas


@app.delete("/cuentas/{user_id}", response_model=schemas.Cliente)
def eliminar_cuenta_por_id(user_id: int, db: Session = Depends(get_db)):
    db_user_deleted = op_monetarias.eliminar_cuenta_por_id(db, user_id)
    if db_user_deleted is False:
        raise HTTPException(status_code=404, detail="Este id de usuario no esta registrado")
    return {"ok": True}


@app.post("/clientes/{user_id}/cuentas", response_model=schemas.Cuenta)
def crear_cuenta(user_id: int, cta: schemas.CuentaRegister, db: Session = Depends(get_db)):
    db_user = op_monetarias.obtener_cliente_por_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="este id de cliente no existe")
    return op_monetarias.crear_cuenta_a_cliente(db=db, id_cliente=user_id, cta=cta)


@app.get("/movimientos/")
def listar_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movimientos = op_monetarias.listar_movimientos(db, skip=skip, limit=limit)
    return movimientos


@app.post("/cliente/{user_id}/movimientos", response_model=schemas.Movimiento)
def crear_movimiento(user_id: int, mvm: schemas.MovimientoRegister, mvmdetalle: schemas.MovimientoDetalleRegister,
                     db: Session = Depends(get_db)):
    db_user = op_monetarias.obtener_cliente_por_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="este id de cliente no existe")
    return op_monetarias.crear_movimiento_a_cliente(db=db, id_cliente=user_id, mvm=mvm, mvmdetalle=mvmdetalle)


@app.get("/movimientos-detalles/")
def listar_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    detalle_movimientos = op_monetarias.listar_detalle_movimientos(db, skip=skip, limit=limit)
    return detalle_movimientos


@app.post("/movimientos/{movimiento_id}/detalle", response_model=schemas.MovimientoDetalle)
def crear_movimiento_detalle(mvm_id: int, mvmdetalle: schemas.MovimientoDetalleRegister,
                             db: Session = Depends(get_db)):
    db_mov = op_monetarias.obtener_movimiento_por_id(db, mvm_id)
    if not db_mov:
        raise HTTPException(status_code=400, detail="este movimiento no existe")
    return op_monetarias.crear_detalle_a_movimiento(db=db, id_movimiento=mvm_id, mvmdetalle=mvmdetalle)

