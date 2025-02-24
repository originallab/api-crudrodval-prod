from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict
from models.models import get_db
from crud.crudDinamico import (
    get_all_records,
    get_record_by_id,
    create_record,
    update_record,
    delete_record,
    patch_record,
)

app = FastAPI()

class DynamicSchema(BaseModel):
    data: Dict  # Permite un diccionario dinámico de campos

# Obtener todos los registros de una tabla
@app.get("/{table_name}/all")
def read_all(table_name: str, db: Session = Depends(get_db)):
    try:
        records = get_all_records(db, table_name)
        return records
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Obtener un registro por su ID
@app.get("/{table_name}/{record_id}")
def read_record_by_id(table_name: str, record_id: int, db: Session = Depends(get_db)):
    try:
        record = get_record_by_id(db, table_name, record_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Crear un nuevo registro
@app.post("/{table_name}")
def create(table_name: str, data: DynamicSchema, db: Session = Depends(get_db)):
    try:
        record_id = create_record(db, table_name, data.data)
        return {"id": record_id, **data.data}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Eliminar un registro
@app.delete("/{table_name}/{record_id}")
def delete(table_name: str, record_id: int, db: Session = Depends(get_db)):
    try:
        deleted = delete_record(db, table_name, record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Record deleted successfully"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Actualizar un registro (PUT)
@app.put("/{table_name}/{record_id}")
def update(
    table_name: str,
    record_id: int,
    data: Dict,
    db: Session = Depends(get_db)
):
    try:
        updated_rows = update_record(db, table_name, record_id, data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Record updated successfully", "updated_rows": updated_rows}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Actualizar parcialmente un registro (PATCH)
@app.patch("/{table_name}/{record_id}")
def patch_record_endpoint(
    table_name: str,
    record_id: int,
    data: Dict,
    db: Session = Depends(get_db)
):
    try:
        updated_rows = patch_record(db, table_name, record_id, data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Record updated partially", "updated_rows": updated_rows}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))