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
    data: Dict

# Obtener un registro por su ID
@app.get("/{table_name}/{record_id}")
def read_record_by_id(table_name: str, record_id: int, db: Session = Depends(get_db)):
    try:
        record = get_valuesid(db, table_name, record_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado en '{table_name}'")
        return {"table": table_name, "record": record}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener todos los registros de una tabla
@app.get("/{table_name}/all")
def read_all(table_name: str, db: Session = Depends(get_db)):
    try:
        records = get_values(db, table_name)
        if not records:
            raise HTTPException(status_code=404, detail=f"No hay registros en la tabla '{table_name}'")
        return {"table": table_name, "records": records}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Crear un nuevo registro
@app.post("/{table_name}")
def create(table_name: str, data: DynamicSchema, db: Session = Depends(get_db)):
    try:
        record_id = create_values(db, table_name, data.data)
        return {"id": record_id, **data.data}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Actualizar completamente un registro (PUT)
@app.put("/{table_name}/{record_id}")
def update(table_name: str, record_id: int, data: DynamicSchema, db: Session = Depends(get_db)):
    try:
        updated_rows = update_values(db, table_name, record_id, data.data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Registro no encontrado o sin cambios")
        return {"message": "Registro actualizado satisfactoriamente"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Actualizar parcialmente un registro (PATCH)
@app.patch("/{table_name}/{record_id}")
def patch_record_endpoint(table_name: str, record_id: int, data: DynamicSchema, db: Session = Depends(get_db)):
    try:
        updated_rows = patch_values(db, table_name, record_id, data.data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="No se encontraron registros para actualizar")
        return {"message": "Registro actualizado parcialmente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Eliminar un registro
@app.delete("/{table_name}/{record_id}")
def delete(table_name: str, record_id: int, db: Session = Depends(get_db)):
    try:
        deleted = delete_values(db, table_name, record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return {"message": "Registro eliminado satisfactoriamente"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
