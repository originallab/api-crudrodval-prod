from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

try:
    # Obtener las variables de entorno
    DB_USER = os.getenv("DB_USER", "botsito")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "botsito123")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "clientesbots")
    
    logger.info(f"Configurando conexión para usuario {DB_USER} en host {DB_HOST}")
    
    # Construcción del string de conexión usando f-string
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    
    # Crear el engine con manejo de errores mejorado
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,               
        max_overflow=10,           
        pool_timeout=30,           
        pool_recycle=3600,         
        pool_pre_ping=True,        
        connect_args={             
            "connect_timeout": 60, 
            "read_timeout": 60,    
            "write_timeout": 60    
        }
    )
    
    # Probar la conexión antes de continuar
    logger.info("Probando conexión a la base de datos...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).fetchone()
            logger.info(f"Conexión a la base de datos exitosa: {result}")
    except Exception as e:
        logger.error(f"Error al probar la conexión inicial: {e}", exc_info=True)
        # No elevar la excepción para permitir que la aplicación continúe
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Metadata para reflejar las tablas existentes
    logger.info("Reflejando tablas de la base de datos...")
    metadata = MetaData()
    try:
        metadata.reflect(bind=engine)
        logger.info(f"Tablas reflejadas: {metadata.tables.keys()}")
    except Exception as e:
        logger.error(f"Error al reflejar las tablas: {e}", exc_info=True)
    
    # Función para obtener una sesión de la base de datos
    def get_db():
        db = SessionLocal()
        try:
            yield db
        except SQLAlchemyError as e:
            logger.error(f"Error durante la sesión de base de datos: {e}", exc_info=True)
            db.rollback()  # Hacer rollback de transacciones pendientes
        finally:
            logger.debug("Cerrando sesión de base de datos")
            db.close()

except Exception as e:
    logger.critical(f"Error crítico durante la configuración de la base de datos: {e}", exc_info=True)
    # Definir un get_db alternativo en caso de error fatal
    def get_db():
        logger.error("Se solicitó una sesión de BD pero hay un error en la configuración")
        raise Exception("No se pudo configurar la conexión a la base de datos")