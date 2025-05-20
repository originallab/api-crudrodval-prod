# Aqui es donde se define la api FastAPI y las rutas
from typing import Optional, Dict
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.models import get_db
from fastapi.middleware.cors import CORSMiddleware


# importacion de los metododos definidos en crud/crudDinamico.py
from crud.crudDinamico import (
    obtener_registros,
    obtener_registros_id,
    crear_registros,
    actualizar_registros,
    eliminar_registros,
    modificar_registros,
    obtener_registros_por_campo,
)

app = FastAPI()

# configuracion de CORS, ya que era un conflicto que se tenia de CORS, permitiendo en direccionamiento de metodos, encabezados, origenes o credenciales.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class DynamicSchema(BaseModel):
    data: Dict


# Este es un metodo que se encarga de verificar que la apikey sea correcta o que la apikey que se esta mandando en el encabezado sea la correcta.
def apikey_validation(db: Session, apikey: str):
    apikeys = obtener_registros(db, 'apikey')
    exists = any(ak["apikey"] == apikey for ak in apikeys)
    if not exists:
        raise HTTPException(status_code=403, detail='Apikey error')

# creacion de ruta GET que sirve para hacer pruebas de que si hay conexion a la api, y si la api esta funcionando correctamente.
@app.get('/health')
def health():
    return {'status': 'ok'}

# Creación de una ruta GET que sirve para traer todos los datos de una tabla
@app.get("/{table_name}/all")
def read_all(
    table_name: str,
    filters: Optional[Dict[str, str]] = None,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey) # En esta parte se tiene que validar lo de la apikey para que sea posible hacer el llamado a la api.
        records = obtener_registros(db, table_name, filters)
        if not records:
            raise HTTPException(status_code=404, detail=f"No hay registros en la tabla '{table_name}'")
        return {"table": table_name, "records": records}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Creación de una ruta get que sirve para traer todos los datos de una tabla, pero filtrando por un campo en especifico.
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
        record = obtener_registros_por_campo(db, table_name, field_name, field_value)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Registro con {field_name}={field_value} no encontrado en '{table_name}'")
        return {"table": table_name, "record": record}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Creacion de una ruta get que sirve para traer todos los datos de una tabla, pero filtrando por un id en especifico.
@app.get("/{table_name}/{record_id}")
def read_record_by_id(
    table_name: str,
    record_id: int,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        print(f"Registro de la tabla: '{table_name}' con unn ID: {record_id}")
        record = obtener_registros_id(db, table_name, record_id)
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

# Creacion de una ruta POST que sirve para crear un nuevo registro en la tabla. 
@app.post("/{table_name}")
def create(
    table_name: str,
    data: DynamicSchema,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        record_id = crear_registros(db, table_name, data.data)
        return {"id": record_id, **data.data}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Creacion de una ruta PUT que sirve para actualizar un registro en la tabla.
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
        updated_rows = actualizar_registros(db, table_name, record_id, data.data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado o sin cambios")
        return {"message": "Registro actualizado satisfactoriamente"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

# Creación de una ruta PATCH que sirve para actualizar parcialmente un registro en la tabla.
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
        updated_rows = modificar_registros(db, table_name, record_id, data.data)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado")
        return {"message": "Registro actualizado parcialmente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Creación de una ruta DELETE que sirve para eliminar un registro en la tabla.
@app.delete("/{table_name}/{record_id}")
def delete(
    table_name: str,
    record_id: int,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        deleted = eliminar_registros(db, table_name, record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado")
        return {"message": "Registro eliminado satisfactoriamente"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))