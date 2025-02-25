from sqlalchemy import Table
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from models.models import metadata, engine

# Método para obtener una tabla por su nombre
def get_table(table_name: str) -> Table:
    if table_name not in metadata.tables:
        raise KeyError(f"Table '{table_name}' not found in metadata.")
    return metadata.tables[table_name]

# Método para obtener todos los registros de una tabla
def get_values(db: Session, table_name: str):
    table = get_table(table_name)
    return db.execute(table.select()).fetchall()

# Método para obtener un registro por su ID
def get_valuesid(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)
    return db.execute(table.select().where(table.c.id == record_id)).fetchone()

# Método para crear un nuevo registro
def create_values(db: Session, table_name: str, data: dict):
    table = get_table(table_name)
    result = db.execute(table.insert().values(**data))
    db.commit()
    return result.lastrowid

# Método para actualizar un registro
def update_values(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)
    result = db.execute(table.update().where(table.c.id == record_id).values(**data))
    db.commit()
    return result.rowcount

# Método para eliminar un registro
def delete_values(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)
    result = db.execute(table.delete().where(table.c.id == record_id))
    db.commit()
    return result.rowcount

# Método para actualizar parcialmente un registro
def patch_values(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)
    result = db.execute(table.update().where(table.c.id == record_id).values(**data))
    db.commit()
    return result.rowcount