from typing import Optional, Dict
from sqlalchemy import Table, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
from models.models import metadata, engine
from fastapi import HTTPException


def get_table(table_name: str):
    if table_name not in metadata.tables:
        metadata.reflect(bind=engine, only=[table_name])
        if table_name not in metadata.tables:
            raise HTTPException(
                status_code=404,
                detail=f"Tabla '{table_name}' no encontrada en la base de datos."
            )
    
    table = metadata.tables[table_name]
    
    # metodo para las pks
    inspector = inspect(engine)
    try:
        pk_info = inspector.get_pk_constraint(table_name)
        if pk_info["constrained_columns"]:
            return table, pk_info["constrained_columns"][0]  # Primera PK encontrada
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener clave primaria: {str(e)}"
        )
  
    column_names = list(table.columns.keys())
    
  
    naming_conventions = [
        f"id_{table_name}",       
        "id",                     
        "uuid",                  
        *[col for col in column_names if col.lower().startswith(("id_", "pk_"))]  
    ]
    
    for col_name in naming_conventions:
        if col_name in column_names:
            return table, col_name
    
    raise HTTPException(
        status_code=400,
        detail=f"No se pudo determinar la clave primaria para la tabla '{table_name}'."
    )


def validate_column(table: Table, column_name: str):
    if column_name not in table.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Columna '{column_name}' no existe en la tabla '{table.name}'."
        )


def get_values(db: Session, table_name: str, filters: Optional[Dict[str, str]] = None):
    table, _ = get_table(table_name)
    try:
        query = table.select()
        if filters:
            conditions = [getattr(table.c, key) == value for key, value in filters.items()]
            query = query.where(and_(*conditions))
        result = db.execute(query).fetchall()
        return [dict(row._mapping) for row in result]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(e)}"
        )

def get_values_by_field(db: Session, table_name: str, field_name: str, field_value: str):
    table, _ = get_table(table_name)
    validate_column(table, field_name)
    try:
        query = table.select().where(getattr(table.c, field_name) == field_value)
        result = db.execute(query).first()
        return dict(result._mapping) if result else None
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(e)}"
        )

def get_valuesid(db: Session, table_name: str, record_id: int):
    table, pk_column = get_table(table_name)
    try:
        query = table.select().where(getattr(table.c, pk_column) == record_id)
        result = db.execute(query).first()
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Registro con ID {record_id} no encontrado."
            )
        return dict(result._mapping)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(e)}"
        )


def create_values(db: Session, table_name: str, data: dict):
    table, pk_column = get_table(table_name)
    try:
        # Eliminar PK si es autoincremental
        if pk_column in data and inspect(table.columns[pk_column]).autoincrement:
            data.pop(pk_column)
        
        result = db.execute(table.insert().values(**data))
        db.commit()
        return result.lastrowid
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear registro: {str(e)}"
        )

def update_values(db: Session, table_name: str, record_id: int, data: dict):
    table, pk_column = get_table(table_name)
    try:
        result = db.execute(
            table.update()
            .where(getattr(table.c, pk_column) == record_id)
            .values(**data)
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Registro no encontrado o sin cambios."
            )
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar: {str(e)}"
        )


def patch_values(db: Session, table_name: str, record_id: int, data: dict):
    return update_values(db, table_name, record_id, data)  # Reutiliza la misma lógica

def delete_values(db: Session, table_name: str, record_id: int):
    table, pk_column = get_table(table_name)
    try:
        result = db.execute(
            table.delete()
            .where(getattr(table.c, pk_column) == record_id)
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Registro no encontrado."
            )
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar: {str(e)}"
        )