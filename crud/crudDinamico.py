from sqlalchemy import Table
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, Table
from models.models import metadata, engine

def get_table(table_name: str) -> Table:
    """Obtiene una tabla dinámica basada en su nombre."""
    return metadata.tables[table_name]

def get_all_records(db: Session, table_name: str):
    """Obtiene todos los registros de una tabla."""
    table = get_table(table_name)
    return db.execute(table.select()).fetchall()

def get_record_by_id(db: Session, table_name: str, record_id: int):
    """Obtiene un registro por su ID."""
    table = get_table(table_name)
    return db.execute(table.select().where(table.c.id == record_id)).fetchone()

def create_record(db: Session, table_name: str, data: dict):
    """Crea un nuevo registro en la tabla."""
    table = get_table(table_name)
    result = db.execute(table.insert().values(**data))
    db.commit()
    return result.lastrowid

def update_record(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)
    result = db.execute(table.update().where(table.c.id == record_id).values(**data))
    db.commit()
    return result.rowcount

def delete_record(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)
    result = db.execute(table.delete().where(table.c.id == record_id))
    db.commit()
    return result.rowcount

def patch_record(db: Session, table_name: str, record_id: int, data: dict):
    """
    Actualiza parcialmente un registro en la tabla basado en su ID.
    Solo se actualizan los campos proporcionados en el diccionario `data`.
    """
    table = get_table(table_name)
    result = db.execute(table.update().where(table.c.id == record_id).values(**data))
    db.commit()
    return result.rowcount

