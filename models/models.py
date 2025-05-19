from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os

DB_USER = os.getenv("DB_USER", "adminUser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "adminUser")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "usuarios")

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
