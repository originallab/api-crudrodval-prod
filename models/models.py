# Este file es para hacer una configuración de la base de datos y sus metadatos

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
import os

# Aqui es donde se hace la configuración con las variables de entorno
DB_USER = os.getenv("DB_USER", "adminUser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "adminUser")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "usuarios")

# Aqui es donde se define la conexion a la base de datos
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

# Solución que encontre para que en la parte del apikey agarrara su id personalizada.
# Esta es una solución muy buena para que no se vea afectada la base de datos
# y no se vea afectada la parte de la api.
apikey_table = Table(
    "apikey",
    metadata,
    Column("id_apikey", Integer, primary_key=True, autoincrement=True),  # PK personalizada
    Column("apikey", String(255), nullable=False),
)

# Este metodo sirve para cargar los datos de las demas tablas (metadata.reflect)
metadata.reflect(bind=engine)  
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()