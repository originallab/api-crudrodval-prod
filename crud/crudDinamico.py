from typing import Optional, Dict
from sqlalchemy import Table, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.models import metadata, engine

# Método para obtener una tabla por su nombre
def get_table(table_name: str) -> Table:
    if table_name not in metadata.tables:
        metadata.reflect(bind=engine)  # Reflejar solo si es necesario
        if table_name not in metadata.tables:
            raise KeyError(f"Table '{table_name}' not found in metadata.")
    return metadata.tables[table_name]

# Método para verificar si una columna existe en la tabla
def validate_column(table: Table, column_name: str):
    if column_name not in table.columns:
        raise KeyError(f"Column '{column_name}' not found in table '{table.name}'.")

# Método para obtener todos los registros de una tabla con filtros opcionales
def get_values(db: Session, table_name: str, filters: Optional[Dict[str, str]] = None):
    table = get_table(table_name)
    try:
        query = table.select()
        if filters:
            # Aplicar filtros dinámicos
            filter_conditions = [getattr(table.c, key) == value for key, value in filters.items()]
            query = query.where(and_(*filter_conditions))
        result = db.execute(query).fetchall()
        return [dict(row._mapping) for row in result]  # Convertir a lista de diccionarios
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {e}")

# Método para obtener un registro por un campo personalizado
def get_values_by_field(db: Session, table_name: str, field_name: str, field_value: str):
    table = get_table(table_name)
    validate_column(table, field_name)  # Validar que la columna exista
    try:
        query = table.select().where(getattr(table.c, field_name) == field_value)
        result = db.execute(query).first()
        return dict(result._mapping) if result else None
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {e}")

# Método para obtener un registro por su ID (usando el campo "id" por defecto)
def get_valuesid(db: Session, table_name: str, record_id: int, primary_key_column: str = "id"):
    table = get_table(table_name)
    validate_column(table, primary_key_column)  # Validar que la columna exista
    try:
        query = table.select().where(getattr(table.c, primary_key_column) == record_id)
        result = db.execute(query).first()
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
def update_values(db: Session, table_name: str, record_id: int, data: dict, primary_key_column: str = "id"):
    table = get_table(table_name)
    validate_column(table, primary_key_column)  # Validar que la columna exista
    existing_record = get_valuesid(db, table_name, record_id, primary_key_column)
    if not existing_record:
        return 0  # No se encontró el registro
    try:
        result = db.execute(
            table.update()
            .where(getattr(table.c, primary_key_column) == record_id)
            .values(**data)
        )
        db.commit()
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {e}")

# Método para actualizar parcialmente un registro (PATCH)
def patch_values(db: Session, table_name: str, record_id: int, data: dict, primary_key_column: str = "id"):
    table = get_table(table_name)
    validate_column(table, primary_key_column)  # Validar que la columna exista
    existing_record = get_valuesid(db, table_name, record_id, primary_key_column)
    if not existing_record:
        return 0  # No se encontró el registro
    try:
        result = db.execute(
            table.update()
            .where(getattr(table.c, primary_key_column) == record_id)
            .values(**data)
        )
        db.commit()
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {e}")

# Método para eliminar un registro
def delete_values(db: Session, table_name: str, record_id: int, primary_key_column: str = "id"):
    table = get_table(table_name)
    validate_column(table, primary_key_column)  # Validar que la columna exista
    existing_record = get_valuesid(db, table_name, record_id, primary_key_column)
    if not existing_record:
        return 0  # No se encontró el registro
    try:
        result = db.execute(
            table.delete()
            .where(getattr(table.c, primary_key_column) == record_id)
        )
        db.commit()
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {e}")