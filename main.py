# python
# !/usr/bin/env python3
from typing import List
# sqlalchemy
from sqlalchemy.orm import Session
# fastapi
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from database import SessionLocal, engine
from models import models
from schemas import schemas

from operations import op_monetarias

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"Challenge": "AdCap"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/v1/clientes/", response_model=List[schemas.Cliente], status_code=status.HTTP_200_OK)
async def listar_todos_los_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = op_monetarias.listar_clientes(db, skip=skip, limit=limit)
    return users


@app.get("/api/v1/clientes/cuentas", status_code=status.HTTP_200_OK, response_model=List[schemas.Cuenta])
async def listar_todos_las_cuentas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cuentas = op_monetarias.listar_cuentas(db, skip=skip, limit=limit)
    return cuentas


@app.get("/api/v1/clientes/{user_id}", status_code=status.HTTP_200_OK, response_model=schemas.Cliente)
async def obtener_cliente_por_id(user_id: int, db: Session = Depends(get_db)):
    db_user = op_monetarias.obtener_cliente_por_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Este id de usuario no esta registrado")
    return db_user


@app.get("/api/v1/cuentas/{id_cuenta}/saldo", status_code=status.HTTP_200_OK)
async def obtener_saldo_cuenta(id_cuenta: int, db: Session = Depends(get_db)):
    cuentas = op_monetarias.consultar_saldo_de_cuenta_cliente(db=db, id_cuenta=id_cuenta)
    return cuentas


@app.post("/api/v1/clientes/", response_model=schemas.Cliente, status_code=status.HTTP_201_CREATED)
async def crear_cliente(cliente: schemas.ClientRegister, db: Session = Depends(get_db)):
    db_user = op_monetarias.obtener_cliente_por_nombre(db, cliente.nombre)
    if db_user:
        raise HTTPException(status_code=400, detail="este nombre de cliente ya esta registrado")
    return op_monetarias.crear_cliente(db=db, cliente=cliente)


@app.post("/api/v1/clientes/{user_id}/cuentas", response_model=schemas.Cuenta, status_code=status.HTTP_200_OK)
async def crear_cuenta(cliente_id: int, cta: schemas.CuentaRegister, db: Session = Depends(get_db)):
    db_user = op_monetarias.obtener_cliente_por_id(db, cliente_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="este id de cliente no existe")
    return op_monetarias.crear_cuenta_a_cliente(db=db, id_cliente=cliente_id, cta=cta)


@app.post("/api/v1/clientes/{id_cuenta}/movimientos", status_code=status.HTTP_201_CREATED)
async def crear_movimiento(id_cuenta: int, mvm: schemas.MovimientoRegister,
                           mvmdetalle: schemas.MovimientoDetalleRegister,
                           db: Session = Depends(get_db)):
    cuenta_asociada = op_monetarias.obtener_cuenta_por_id(db, id_cuenta)
    if not cuenta_asociada:
        raise HTTPException(status_code=400, detail="este id de cuenta no existe")
    return op_monetarias.crear_movimiento_a_cuenta(db=db, id_cuenta=id_cuenta, mvm=mvm, mvmdetalle=mvmdetalle)


@app.put("/api/v1/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_cliente_por_id(cliente_id: int, nombre: str, db: Session = Depends(get_db)):
    db_user = op_monetarias.obtener_cliente_por_id(db, cliente_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="este id de cliente no existe")
    return op_monetarias.actualizar_cliente(db=db,nombre_nuevo=nombre,cliente_id=cliente_id)


@app.get("/api/v1/movimientos/", status_code=status.HTTP_200_OK)
async def listar_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movimientos = op_monetarias.listar_movimientos(db, skip=skip, limit=limit)
    return movimientos


@app.get("/api/v1/movimiento-detalle/", status_code=status.HTTP_200_OK)
async def listar_detalles_movimiento(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    detalle_movimientos = op_monetarias.listar_detalle_movimientos(db, skip=skip, limit=limit)
    return detalle_movimientos


@app.delete("/api/v1/clientes/{user_id}", status_code=status.HTTP_200_OK)
async def eliminar_cliente_por_id(user_id: int, db: Session = Depends(get_db)):
    db_user_deleted = op_monetarias.eliminar_cliente_por_id(db, user_id)
    if not db_user_deleted:
        raise HTTPException(status_code=404, detail="Este id de usuario no esta registrado")
    return {"mensaje": f"cliente eliminado correctamente"}


@app.delete("/api/v1/cuentas/{user_id}", status_code=status.HTTP_200_OK)
async def eliminar_cuenta_por_id(user_id: int, db: Session = Depends(get_db)):
    db_user_deleted = op_monetarias.eliminar_cuenta_por_id(db, user_id)
    if not db_user_deleted:
        raise HTTPException(status_code=404, detail="Este id de usuario no esta registrado")
    return {"mensaje": f"cuenta eliminada correctamente"}


@app.delete("/api/v1/movimiento-detalles/{id_movimiento_detalle}", status_code=status.HTTP_200_OK)
async def eliminar_movimiento_detalle(id_movimiento_detalle: int, db: Session = Depends(get_db)):
    db_user_deleted = op_monetarias.eliminar_movimiento_detalle_por_id(db=db,
                                                                       id_movimiento_detalle=id_movimiento_detalle)
    if db_user_deleted is False:
        raise HTTPException(status_code=404, detail="Id de movimiento no encontrado")
    return {"detalle": "movimiento eliminado"}
