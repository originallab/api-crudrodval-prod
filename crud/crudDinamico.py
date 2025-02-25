from sqlalchemy import Table, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from models.models import metadata

# Método para obtener una tabla por su nombre
def get_table(table_name: str) -> Table:
    if table_name not in metadata.tables:
        raise KeyError(f"Table '{table_name}' not found in metadata.")
    return metadata.tables[table_name]

# Método para obtener todos los registros de una tabla
def get_values(db: Session, table_name: str):
    try:
        table = get_table(table_name)
        records = db.execute(select(table)).fetchall()
        if not records:
            raise HTTPException(status_code=404, detail=f"No se encuentran valores en la tabla '{table_name}'")
        return records
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {e}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Método para obtener un registro por su ID
def get_valuesid(db: Session, table_name: str, record_id: int):
    try:
        table = get_table(table_name)
        if 'id' not in table.columns:
            raise HTTPException(status_code=400, detail=f"Table '{table_name}' does not have an 'id' column")
        record = db.execute(select(table).where(table.c.id == record_id)).fetchone()
        if record is None:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no se encuentra en la tabla '{table_name}'")
        return record
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {e}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Método para actualizar parcialmente un registro
def patch_values(db: Session, table_name: str, record_id: int, data: dict):
    try:
        table = get_table(table_name)
        if 'id' not in table.columns:
            raise HTTPException(status_code=400, detail=f"Table '{table_name}' does not have an 'id' column")
        
        # Verificar si el registro existe
        existing_record = db.execute(select(table).where(table.c.id == record_id)).fetchone()
        if existing_record is None:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no se encuentra en la tabla '{table_name}'")

        # Actualizar el registro
        result = db.execute(table.update().where(table.c.id == record_id).values(**data))
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="No records were updated")
        return result.rowcount
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {e}")
    except SQLAlchemyError as e:
        db.rollback()  # Revertir la transacción en caso de error
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")