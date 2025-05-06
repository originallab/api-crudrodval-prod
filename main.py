from typing import Optional, Dict
from fastapi import FastAPI, Depends, HTTPException, Header, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from pydantic import BaseModel
import logging
import traceback
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

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

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

# Middleware para capturar excepciones globales
@app.middleware("http")
async def db_exception_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except OperationalError as e:
        logger.error(f"Error de conexión a la base de datos: {e}")
        return JSONResponse(
            status_code=503,
            content={"detail": "Error de conexión a la base de datos. Por favor, inténtelo más tarde."}
        )
    except SQLAlchemyError as e:
        logger.error(f"Error SQLAlchemy: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Error en la base de datos"}
        )
    except Exception as e:
        logger.error(f"Error no manejado: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor"}
        )

# Evento de inicio para probar la conexión
@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando aplicación...")
    try:
        # Intentar obtener una conexión a la base de datos
        db = next(get_db())
        db.execute("SELECT 1")
        logger.info("Conexión a la base de datos establecida correctamente")
        db.close()
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos durante el inicio: {e}")
        # No elevar la excepción para permitir que la aplicación continúe

def apikey_validation(db: Session, apikey: str):
    try:
        if apikey is None:
            raise HTTPException(status_code=401, detail="API key requerida")
        
        apikeys = get_values(db, 'apikey')
        exists = any(ak["apikey"] == apikey for ak in apikeys)
        if not exists:
            raise HTTPException(status_code=403, detail='API key inválida')
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en la validación de API key: {e}")
        raise HTTPException(status_code=503, detail="Error en la validación de API key")
    except Exception as e:
        logger.error(f"Error durante la validación de API key: {e}")
        raise HTTPException(status_code=500, detail="Error interno en la validación")

@app.get('/health')
def health():
    return {'status': 'ok'}

# Ruta para probar la conexión a la base de datos
@app.get('/test-db')
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT 1").fetchone()
        return {"database": "connected", "result": result[0]}
    except Exception as e:
        logger.error(f"Error al probar la conexión a la base de datos: {e}")
        raise HTTPException(status_code=503, detail=f"Error de conexión: {str(e)}")

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
    except HTTPException:
        raise
    except KeyError as e:
        logger.error(f"KeyError en read_all: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en read_all: {e}")
        raise HTTPException(status_code=503, detail="Error en la conexión a la base de datos")
    except Exception as e:
        logger.error(f"Error inesperado en read_all: {e}")
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
    except HTTPException:
        raise
    except KeyError as e:
        logger.error(f"KeyError en read_record_by_field: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en read_record_by_field: {e}")
        raise HTTPException(status_code=503, detail="Error en la conexión a la base de datos")
    except Exception as e:
        logger.error(f"Error inesperado en read_record_by_field: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Obtener un registro por su clave primaria dinámica
@app.get("/{table_name}/{record_id}")
def read_record_by_id(
    table_name: str,
    record_id: int,
    db: Session = Depends(get_db),
    apikey: str = Header(None)
):
    try:
        apikey_validation(db, apikey)
        logger.info(f"Obteniendo registro de tabla '{table_name}' con ID {record_id}")
        record = get_valuesid(db, table_name, record_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado en '{table_name}'")
        return {"table": table_name, "record": record}
    except HTTPException:
        raise
    except KeyError as e:
        logger.error(f"KeyError en read_record_by_id: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en read_record_by_id: {e}")
        raise HTTPException(status_code=503, detail="Error en la conexión a la base de datos")
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error inesperado en read_record_by_id: {e}")
        logger.error(f"Traza completa:\n{error_trace}")
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
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en create: {e}")
        raise HTTPException(status_code=503, detail="Error en la conexión a la base de datos")
    except Exception as e:
        logger.error(f"Error inesperado en create: {e}")
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
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en update: {e}")
        raise HTTPException(status_code=503, detail="Error en la conexión a la base de datos")
    except Exception as e:
        logger.error(f"Error inesperado en update: {e}")
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
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en patch: {e}")
        raise HTTPException(status_code=503, detail="Error en la conexión a la base de datos")
    except Exception as e:
        logger.error(f"Error inesperado en patch: {e}")
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
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en delete: {e}")
        raise HTTPException(status_code=503, detail="Error en la conexión a la base de datos")
    except Exception as e:
        logger.error(f"Error inesperado en delete: {e}")
        raise HTTPException(status_code=422, detail=str(e))