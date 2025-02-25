from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict
from models.models import get_db
from crud.crudDinamico import (
    get_values,
    get_valuesid,
    create_values,
    update_values,
    delete_values,
    patch_values,
)

app = FastAPI()

class DynamicSchema(BaseModel):
    data: Dict  # Permite un diccionario dinámico de campos

# Obtener todos los registros de una tabla
@app.get("/{table_name}/all")
def read_all(table_name: str, db: Session = Depends(get_db)):
    try:
        records = get_values(db, table_name)
        if not records:
            raise HTTPException(status_code=404, detail=f"No se encuentran valores en la tabla '{table_name}'")
        return {"table": table_name, "records": records}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Obtener un registro por su ID
@app.get("/{table_name}/{record_id}")
def read_record_by_id(table_name: str, record_id: int, db: Session = Depends(get_db)):
    try:
        record = get_valuesid(db, table_name, record_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no se encuentra en la tabla '{table_name}'")
        return {"table": table_name, "record": record}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Crear un nuevo registro
@app.post("/{table_name}")
def create(table_name: str, data: DynamicSchema, db: Session = Depends(get_db)):
    try:
        record_id = create_values(db, table_name, data.data)
        return {"id": record_id, **data.data}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Eliminar un registro
@app.delete("/{table_name}/{record_id}")
def delete(table_name: str, record_id: int, db: Session = Depends(get_db)):
    try:
        deleted = delete_values(db, table_name, record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return {"message": "Registro eliminado satisfactoriamente"}
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
        updated_rows = update_values(db, table_name, record_id, data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Registros actualizados satisfactoriamente", "updated_rows": updated_rows}
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
        # Verificar si el registro existe antes de actualizar
        existing_record = get_valuesid(db, table_name, record_id)
        if existing_record is None:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no se encuentra en la tabla '{table_name}'")

        # Actualizar el registro
        updated_rows = patch_values(db, table_name, record_id, data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="No records were updated")

        # Obtener el registro actualizado para devolverlo
        updated_record = get_valuesid(db, table_name, record_id)
        return {"message": "Registro actualizado de manera parcial", "Registro actualizado": updated_record}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")