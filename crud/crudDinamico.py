from sqlalchemy import Table
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from models.models import metadata, engine

# METODOS PARA EL MANEJO DEL CRUD DE LA API

# Metodo get para obtener una tabla a traves de su nombre, es un metodo general para traer los datos en todos los metodos
def get_table(table_name: str) -> Table:
    if table_name not in metadata.tables:
        raise KeyError(f"Table '{table_name}' not found in metadata.")
    return metadata.tables[table_name]

# Metodo get para obtener todos los valores de una tabla.
def get_values(db: Session, table_name: str):
    table = get_table(table_name)
    return db.execute(table.select()).fetchall()

# Metodo get para traer registros de una tabla por medio de su id.
def get_valuesid(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)
    return db.execute(table.select().where(table.c.id == record_id)).fetchone()

# metodo para crear un nuevo registro en una tabla
def create_values(db: Session, table_name: str, data: dict):
    table = get_table(table_name)
    result = db.execute(table.insert().values(**data))
    db.commit()
    return result.lastrowid

# metodo para modificar un registro en la tabla
def update_values(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)
    result = db.execute(table.update().where(table.c.id == record_id).values(**data))
    db.commit()
    return result.rowcount

# metodo para eliminar un registro de una tabla
def delete_values(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)
    result = db.execute(table.delete().where(table.c.id == record_id))
    db.commit()
    return result.rowcount

# metodo para hacer una actualizacion de solo un campo en un tabla por medio de su id
def patch_values(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)
    result = db.execute(table.update().where(table.c.id == record_id).values(**data))
    db.commit()
    return result.rowcount