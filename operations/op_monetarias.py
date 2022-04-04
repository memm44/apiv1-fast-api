from sqlalchemy.orm import Session
import time
from models import models
from schemas import schemas
from fastapi import HTTPException


# Clientes ================================================================
def crear_cliente(db: Session, cliente: schemas.ClientRegister):
    db_user = models.Cliente(nombre=cliente.nombre)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def listar_clientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cliente).offset(skip).limit(limit).all()


def obtener_cliente_por_id(db: Session, id_cliente: int):
    return db.query(models.Cliente).filter(models.Cliente.id == id_cliente).first()


def obtener_movimiento_por_id(db: Session, id_movimiento: int):
    return db.query(models.Movimiento).filter(models.Movimiento.id == id_movimiento).first()


def obtener_movimiento_detalle_por_id(db: Session, id_movimiento_detalle: int):
    return db.query(models.MovimientoDetalle).filter(models.MovimientoDetalle.id == id_movimiento_detalle).first()


def actualizar_cliente(db: Session, nombre_nuevo:str, cliente_id: int):
    cliente = obtener_cliente_por_id(db=db, id_cliente=cliente_id)
    cliente.nombre= nombre_nuevo
    db.add(cliente)
    db.commit()
    return cliente


def eliminar_cliente_por_id(db: Session, id_cliente: int):
    para_borrar = db.query(models.Cliente).filter(models.Cliente.id == id_cliente).first()
    if para_borrar:
        db.delete(para_borrar)
        db.commit()
    return para_borrar


# Cuentas=======================================================

def eliminar_cuenta_por_id(db: Session, id_cuenta: int):
    para_borrar = db.query(models.Cuenta).filter(models.Cuenta.id == id_cuenta).first()
    if para_borrar:
        db.delete(para_borrar)
        db.commit()
    return para_borrar


def consultar_saldo_de_cuenta_cliente(db: Session, id_cuenta: int):
    cuenta = obtener_cuenta_por_id(db=db, id_cuenta=id_cuenta)
    return {
        "saldo_disponible": cuenta.saldo_disponible
    }


def listar_cuentas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cuenta).offset(skip).limit(limit).all()


def obtener_cuenta_por_id(db: Session, id_cuenta: int):
    return db.query(models.Cuenta).filter(models.Cuenta.id == id_cuenta).first()


def sumar_saldo_a_cuenta(db: Session, id_cuenta: int, saldo):
    cuenta_seleccionada = db.query(models.Cuenta).filter(models.Cuenta.id == id_cuenta).first()
    cuenta_seleccionada.saldo_disponible += saldo
    db.commit()
    db.refresh(cuenta_seleccionada)
    return {"id_cuenta": id_cuenta, "saldo_agregado": saldo, "detalle": "Operacion exitosa!"}


def es_apto_para_debito(db: Session, id_cuenta: int, saldo_a_debitar: float):
    cuenta_seleccionada = db.query(models.Cuenta).filter(models.Cuenta.id == id_cuenta).first()
    return saldo_a_debitar <= cuenta_seleccionada.saldo_disponible


def restar_saldo_a_cuenta(db: Session, id_cuenta: int, saldo):
    cuenta_seleccionada = db.query(models.Cuenta).filter(models.Cuenta.id == id_cuenta).first()
    if not es_apto_para_debito(db=db, id_cuenta=id_cuenta, saldo_a_debitar=saldo):
        raise HTTPException(status_code=400, detail="el saldo es insuficiente")
    cuenta_seleccionada.saldo_disponible -= saldo
    db.commit()
    db.refresh(cuenta_seleccionada)
    return {"saldo_debitado": saldo, "detalle": "Operacion exitosa!"}


def crear_cuenta_a_cliente(db: Session, cta: schemas.CuentaRegister, id_cliente: int):
    db_cuenta = models.Cuenta(**cta.dict(), cliente_id=id_cliente)
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


def validar_operacion(db: Session, tipo_operacion: str, id_cuenta: int, saldo: float):
    if tipo_operacion.lower() == "ingreso":
        return sumar_saldo_a_cuenta(db=db, id_cuenta=id_cuenta, saldo=saldo)
    elif tipo_operacion.lower() == "egreso":
        return restar_saldo_a_cuenta(db=db, id_cuenta=id_cuenta, saldo=saldo)
    else:
        return None


def obtener_cliente_por_nombre(db: Session, nombre_cliente: str):
    return db.query(models.Cliente).filter(models.Cliente.nombre == nombre_cliente).first()


# Movimientos =================================================================


def crear_movimiento_a_cuenta(db: Session, mvm: schemas.MovimientoRegister,
                              mvmdetalle: schemas.MovimientoDetalleRegister, id_cuenta: int):
    operacion = validar_operacion(db=db, tipo_operacion=mvmdetalle.tipo, id_cuenta=id_cuenta, saldo=mvmdetalle.importe)
    if not operacion:
        return {"error": "operacion invalida"}
    db_movimiento = models.Movimiento(**mvm.dict(), cuenta_id=id_cuenta)
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    crear_detalle_a_movimiento(db=db, mvmdetalle=mvmdetalle, id_movimiento=db_movimiento.id)
    return operacion


def eliminar_movimiento_por_id(db: Session, id_movimiento: int):
    para_borrar = obtener_movimiento_por_id(db=db, id_movimiento=id_movimiento)
    db.delete(para_borrar)
    db.commit()
    return para_borrar


def eliminar_movimiento_detalle_por_id(db: Session, id_movimiento_detalle: int):
    restaurar_saldo_a_cuenta(db=db, id_movimiento_detalle=id_movimiento_detalle)
    para_borrar = obtener_movimiento_detalle_por_id(db=db, id_movimiento_detalle=id_movimiento_detalle)
    db.delete(para_borrar)
    db.commit()
    return para_borrar


def restaurar_saldo_a_cuenta(db: Session, id_movimiento_detalle: int):
    movimiento_detalle = obtener_movimiento_detalle_por_id(db=db, id_movimiento_detalle=id_movimiento_detalle)
    movimiento = obtener_movimiento_por_id(db=db, id_movimiento=movimiento_detalle.movimiento_id)
    cuenta = obtener_cuenta_por_id(db=db, id_cuenta=movimiento.cuenta_id)
    print(movimiento_detalle.tipo)
    print(movimiento.__dict__)
    print(cuenta.id)
    time.sleep(10)
    if movimiento:
        if movimiento_detalle.tipo.lower() == "egreso":
            return sumar_saldo_a_cuenta(db=db, id_cuenta=cuenta.id, saldo=movimiento_detalle.importe)


# Movimiento Detalles =========================================================

def listar_detalle_movimientos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MovimientoDetalle).offset(skip).limit(limit).all()


def crear_detalle_a_movimiento(db: Session, mvmdetalle: schemas.MovimientoDetalleRegister, id_movimiento: int):
    db_movimiento = models.MovimientoDetalle(**mvmdetalle.dict(), movimiento_id=id_movimiento)
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento


def listar_movimientos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Movimiento).offset(skip).limit(limit).all()
