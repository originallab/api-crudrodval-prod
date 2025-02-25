from sqlalchemy import Table
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.models import metadata, engine

# Método para obtener una tabla por su nombre
def get_table(table_name: str) -> Table:
    # Asegurar que las tablas están reflejadas correctamente
    if table_name not in metadata.tables:
        metadata.reflect(bind=engine)  # Reflejar solo si es necesario
        if table_name not in metadata.tables:
            raise KeyError(f"Table '{table_name}' not found in metadata.")
    return metadata.tables[table_name]

# Método para obtener todos los registros de una tabla
def get_values(db: Session, table_name: str):
    table = get_table(table_name)
    try:
        result = db.execute(table.select()).fetchall()
        return [dict(row._mapping) for row in result]  # Convertir a lista de diccionarios
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {e}")

# Método para obtener un registro por su ID
def get_valuesid(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)
    try:
        result = db.execute(table.select().where(table.c.id == record_id)).first()
        return dict(result._mapping) if result else None
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {e}")

# Método para crear un nuevo registro
def create_values(db: Session, table_name: str, data: dict):
    table = get_table(table_name)
    try:
        result = db.execute(table.insert().values(**data))
        db.commit()
        return result.lastrowid
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {e}")

# Método para actualizar completamente un registro (PUT)
def update_values(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)
    existing_record = get_valuesid(db, table_name, record_id)
    if not existing_record:
        return 0  # No se encontró el registro
    try:
        result = db.execute(table.update().where(table.c.id == record_id).values(**data))
        db.commit()
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {e}")

# Método para actualizar parcialmente un registro (PATCH)
def patch_values(db: Session, table_name: str, record_id: int, data: dict):
    table = get_table(table_name)
    existing_record = get_valuesid(db, table_name, record_id)
    if not existing_record:
        return 0  # No se encontró el registro
    try:
        result = db.execute(table.update().where(table.c.id == record_id).values(**data))
        db.commit()
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {e}")

# Método para eliminar un registro
def delete_values(db: Session, table_name: str, record_id: int):
    table = get_table(table_name)
    existing_record = get_valuesid(db, table_name, record_id)
    if not existing_record:
        return 0  # No se encontró el registro
    try:
        result = db.execute(table.delete().where(table.c.id == record_id))
        db.commit()
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {e}")
