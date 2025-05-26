from typing import Optional, Dict
from sqlalchemy import Table, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
from models.models import metadata, engine
from datetime import datetime  # Importar datetime para manejar fechas

# Método para obtener una tabla por su nombre y su clave primaria
def get_table(table_name: str):
    # Asegurar que la tabla existe o reflejarla
    if table_name not in metadata.tables:
        metadata.clear()
        metadata.reflect(bind=engine)
        if table_name not in metadata.tables:
            raise KeyError(f"Tabla '{table_name}' no encontrada en metadata.")
    
    table = metadata.tables[table_name]
    column_names = list(table.columns.keys())
    
    # Paso 1: Buscar columna exacta id_{table_name}
    possible_id = f"id_{table_name}"
    if possible_id in column_names:
        return table, possible_id
    
    # Paso 2: Buscar ignorando mayúsculas/minúsculas
    for col in column_names:
        if col.lower() == possible_id.lower():
            return table, col
    
    # Paso 3: Buscar cualquier columna que comience con id_ o ID_
    for prefix in ['id_', 'ID_']:
        id_columns = [col for col in column_names if col.startswith(prefix)]
        if id_columns:
            return table, id_columns[0]
    
    # Paso 4: Usar las claves primarias si existen
    primary_key_columns = inspect(table).primary_key.columns.keys()
    if primary_key_columns:
        return table, primary_key_columns[0]
    
    # Paso 5: Buscar una columna llamada simplemente 'id' o 'ID'
    for id_name in ['id', 'ID']:
        if id_name in column_names:
            return table, id_name
    
    # Si llegamos aquí, no se encontró una columna adecuada
    raise KeyError(f"No se pudo encontrar la clave primaria para la tabla '{table_name}'.")

# Método para verificar si una columna existe en la tabla
def validate_column(table: Table, column_name: str):
    if column_name not in table.columns:
        raise KeyError(f"Column '{column_name}' not found in table '{table.name}'.")

# Método para obtener todos los registros de una tabla con filtros opcionales
def get_values(db: Session, table_name: str, filters: Optional[Dict[str, str]] = None):
    table, _ = get_table(table_name)  # Obtener la tabla (no necesitamos la clave primaria aquí)
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
    table, _ = get_table(table_name)  # Obtener la tabla (no necesitamos la clave primaria aquí)
    validate_column(table, field_name)  # Validar que la columna exista
    try:
        query = table.select().where(getattr(table.c, field_name) == field_value)
        result = db.execute(query).first()
        return dict(result._mapping) if result else None
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {e}")

# Método para obtener un registro por su ID (usando la clave primaria dinámica)
def get_valuesid(db: Session, table_name: str, record_id: int):
    table, primary_key_column = get_table(table_name)
    
    try:
        # Crear una consulta explícita para mayor claridad
        column = getattr(table.c, primary_key_column)
        query = table.select().where(column == record_id)
        
        # Ejecutar la consulta directamente (sin usar ORM)
        result = db.execute(query).first()
        
        if result is None:
            return None
            
        # Convertir el resultado a un diccionario
        return dict(result._mapping)
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error de base de datos: {str(e)}")
    

# Método para crear un nuevo registro
def create_values(db: Session, table_name: str, data: dict):
    table, primary_key_column = get_table(table_name)  # Obtener la tabla y la clave primaria
    try:
        result = db.execute(table.insert().values(**data))
        db.commit()
        return result.lastrowid  # Devuelve el ID generado automáticamente
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {e}")
    
# Método para actualizar completamente un registro (PUT)
def update_values(db: Session, table_name: str, record_id: int, data: dict):
    table, primary_key_column = get_table(table_name)  # Obtener la tabla y la clave primaria
    try:
        # Asegúrate de que la fecha de última modificación se incluya en los datos
        if 'ultima_modificacion' not in data:
            data['ultima_modificacion'] = datetime.utcnow()  # Establecer la fecha actual si no se proporciona

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
def patch_values(db: Session, table_name: str, record_id: int, data: dict):
    table, primary_key_column = get_table(table_name)  # Obtener la tabla y la clave primaria
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
def delete_values(db: Session, table_name: str, record_id: int):
    table, primary_key_column = get_table(table_name)  # Obtener la tabla y la clave primaria
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
