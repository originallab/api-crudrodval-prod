from sqlalchemy import Table
from sqlalchemy.orm import Session
from models.models import metadata

# Obtener la tabla dinámicamente
def get_table(table_name: str) -> Table:
    if table_name not in metadata.tables:
        raise KeyError(f"Table '{table_name}' not found in metadata.")
    return metadata.tables[table_name]

# Obtener todos los registros de una tabla
def get_values(db: Session, table_name: str):
    table = get_table(table_name)
    return db.execute(table.select()).fetchall()  # Se eliminó .scalars()

# Obtener un registro por su ID
def get_valuesid(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)
    return db.execute(table.select().where(table.c.id == record_id)).fetchone()

# Crear un nuevo registro
def create_values(db: Session, table_name: str, data: dict):
    table = get_table(table_name)
    result = db.execute(table.insert().values(**data))
    db.commit()
    return result.lastrowid

# Actualizar completamente un registro (PUT)
def update_values(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)

    existing_record = get_valuesid(db, table_name, record_id)
    if not existing_record:
        return 0  # Indicar que no se actualizó ningún registro

    result = db.execute(table.update().where(table.c.id == record_id).values(**data))
    db.commit()
    return result.rowcount

# Actualizar parcialmente un registro (PATCH)
def patch_values(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)

    result = db.execute(table.update().where(table.c.id == record_id).values(**data))
    db.commit()
    return result.rowcount

# Eliminar un registro
def delete_values(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)

    existing_record = get_valuesid(db, table_name, record_id)
    if not existing_record:
        return 0  # Indicar que no se eliminó ningún registro

    result = db.execute(table.delete().where(table.c.id == record_id))
    db.commit()
    return result.rowcount
