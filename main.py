from typing import Optional, Dict
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.models import get_db
from fastapi.middleware.cors import CORSMiddleware
from crud.crudDinamico import (
    get_values,
    get_valuesid,
    create_values,
    update_values,
    delete_values,
    patch_values,
    get_values_by_field,
)

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes (cambia esto en producción)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

class DynamicSchema(BaseModel):
    data: Dict

def apikey_validation(db: Session, apikey: str):
    apikeys = get_values(db, 'apikey')
    exists = any(ak["apikey"] == apikey for ak in apikeys)
    if not exists:
        raise HTTPException(status_code=403, detail='Apikey error')

@app.get('/health')
def health():
    return {'status': 'ok'}

# Obtener todos los registros de una tabla con filtros opcionales
@app.get("/{table_name}/all")
def read_all(
    table_name: str,
    filters: Optional[Dict[str, str]] = None,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        records = get_values(db, table_name, filters)
        if not records:
            raise HTTPException(status_code=404, detail=f"No hay registros en la tabla '{table_name}'")
        return {"table": table_name, "records": records}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener un registro por un campo personalizado (no clave primaria)
@app.get("/{table_name}/field/{field_name}/{field_value}")
def read_record_by_field(
    table_name: str,
    field_name: str,
    field_value: str,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        record = get_values_by_field(db, table_name, field_name, field_value)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Registro con {field_name}={field_value} no encontrado en '{table_name}'")
        return {"table": table_name, "record": record}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener un registro por su clave primaria dinámica
# En el archivo de la API (FastAPI)
@app.get("/{table_name}/{record_id}")
def read_record_by_id(
    table_name: str,
    record_id: int,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        print(f"Obteniendo registro de tabla '{table_name}' con ID {record_id}")
        record = get_valuesid(db, table_name, record_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado en '{table_name}'")
        return {"table": table_name, "record": record}
    except KeyError as e:
        print(f"Error KeyError: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error interno: {str(e)}")
        print(f"Traza completa:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
# Crear un nuevo registro
@app.post("/{table_name}")
def create(
    table_name: str,
    data: DynamicSchema,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        record_id = create_values(db, table_name, data.data)
        return {"id": record_id, **data.data}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Actualizar completamente un registro
@app.put("/{table_name}/{record_id}")
def update(
    table_name: str,
    record_id: int,
    data: DynamicSchema,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        updated_rows = update_values(db, table_name, record_id, data.data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado o sin cambios")
        return {"message": "Registro actualizado satisfactoriamente"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Actualizar parcialmente un registro
@app.patch("/{table_name}/{record_id}")
def patch(
    table_name: str,
    record_id: int,
    data: DynamicSchema,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        updated_rows = patch_values(db, table_name, record_id, data.data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado")
        return {"message": "Registro actualizado parcialmente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Eliminar un registro
@app.delete("/{table_name}/{record_id}")
def delete(
    table_name: str,
    record_id: int,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        deleted = delete_values(db, table_name, record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado")
        return {"message": "Registro eliminado satisfactoriamente"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))