from sqlalchemy.orm import Session

from models import models
from schemas import schemas


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


def eliminar_cliente_por_id(db: Session, id_cliente: int):
    para_borrar = db.query(models.Cliente).filter(models.Cliente.id == id_cliente).first()
    db.delete(para_borrar)
    db.commit()
    db.refresh(para_borrar)
    return para_borrar


# Cuentas=======================================================

def eliminar_cuenta_por_id(db: Session, id_cuenta: int):
    para_borrar = db.query(models.Cuenta).filter(models.Cuenta.id == id_cuenta).first()
    db.delete(para_borrar)
    db.commit()
    return para_borrar


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
        return {"id_cuenta": id_cuenta, "saldo_debitado": 0, "detalle": "Saldo insuficiente!"}
    cuenta_seleccionada.saldo_disponible -= saldo
    db.commit()
    db.refresh(cuenta_seleccionada)
    return {"id_cuenta": id_cuenta, "saldo_debitado": saldo, "detalle": "Operacion exitosa!"}


def crear_cuenta_a_cliente(db: Session, cta: schemas.CuentaRegister, id_cliente: int):
    db_cuenta = models.Cuenta(**cta.dict(), cliente_id=id_cliente)
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


def realizar_operacion(db: Session, tipo_operacion: str, id_cuenta: int, saldo: float):
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
    if realizar_operacion(db=db, tipo_operacion=mvmdetalle.tipo, id_cuenta=id_cuenta,
                          saldo=mvmdetalle.importe) is False:
        return {"error": "el tipo de operación no es valida"}
    db_movimiento = models.Movimiento(**mvm.dict(), cuenta_id=id_cuenta)
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    crear_detalle_a_movimiento(db=db, mvmdetalle=mvmdetalle, id_movimiento=db_movimiento.id)

    return db_movimiento


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
