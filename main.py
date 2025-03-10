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
)

app = FastAPI()

class DynamicSchema(BaseModel):
    data: Dict  # Permite un diccionario dinámico de campos


@app.get("/{table_name}")
def read_all(table_name: str, db: Session = Depends(get_db)):
    try:
        records = get_all_records(db, table_name)
        return records
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/{table_name}")
def create(table_name: str, data: DynamicSchema, db: Session = Depends(get_db)):
    try:
        record_id = create_record(db, table_name, data.data)
        return {"id": record_id, **data.data}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    

@app.delete("/{table_name}/{record_id}")
def delete(table_name: str, record_id: int, db: Session = Depends(get_db)):
    try:
        # Llama a la función delete_record para eliminar el registro
        deleted = delete_record(db, table_name, record_id)
        
        # Si no se encontró el registro, lanza una excepción 404
        if not deleted:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Retorna un mensaje de éxito
        return {"message": "Record deleted successfully"}
    
    except KeyError as e:
        # Maneja errores de clave (por ejemplo, tabla no encontrada)
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        # Maneja otros errores inesperados
        raise HTTPException(status_code=422, detail=str(e))

@app.put("/{table_name}/{record_id}")  # Usa PUT para actualizaciones
def update(
    table_name: str,
    record_id: int,
    data: Dict,  # Recibe el cuerpo de la solicitud como un diccionario
    db: Session = Depends(get_db)  # Inyecta la sesión de la base de datos
):
    try:
        # Llama a la función update_record para actualizar el registro
        updated_rows = update_record(db, table_name, record_id, data)
        
        # Si no se encontró el registro, lanza una excepción 404
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Retorna un mensaje de éxito
        return {"message": "Record updated successfully", "updated_rows": updated_rows}
    
    except KeyError as e:
        # Maneja errores de clave (por ejemplo, tabla no encontrada)
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        # Maneja otros errores inesperados
        raise HTTPException(status_code=422, detail=str(e))


@app.patch("/{table_name}/{record_id}")
async def patch_record_endpoint(table_name: str, record_id: int, data: dict):
    db = SessionLocal()  # Obtén la sesión de la base de datos
    updated_rows = patch_record(db, table_name, record_id, data)
    db.close()

    if updated_rows == 0:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    return {"message": "Registro actualizado parcialmente"}

# Nuevo endpoint para probar la conexión a la base de datos
@app.get("/test-db-connection")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # Intenta realizar una consulta simple
        db.execute("SELECT 1")
        return {"message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))