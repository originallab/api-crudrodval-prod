from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os

<<<<<<< HEAD
# Cargar variables de entorno desde el archivo .env

# Obtener las variables de entorno
DB_USER = os.getenv("DB_USER","cosmetica1")
DB_PASSWORD = os.getenv("DB_PASSWORD","neurone123")
DB_HOST = os.getenv("DB_HOST","localhost")
DB_NAME = os.getenv("DB_NAME","neuronecosmetica")
=======
DB_USER = os.getenv("DB_USER", "logisticaRODVAL")
DB_PASSWORD = os.getenv("DB_PASSWORD", "logisticaRODVAL")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "rodval")
>>>>>>> ddf8e1b73cdd1968089646dda5ae320705cbeea6

# Construcción del string de conexión usando f-string
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Metadata para reflejar las tablas existentes
metadata = MetaData()
metadata.reflect(bind=engine)


# Función para obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()