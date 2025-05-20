from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
import os

DB_USER = os.getenv("DB_USER", "adminUser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "adminUser")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "usuarios")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

# 👇 Definición MANUAL de la tabla `apikey` para forzar `id_apikey` como PK
apikey_table = Table(
    "apikey",
    metadata,
    Column("id_apikey", Integer, primary_key=True, autoincrement=True),  # PK personalizada
    Column("apikey", String(255), nullable=False),
)

# Reflejar el resto de tablas automáticamente (opcional)
metadata.reflect(bind=engine)  # 👈 Esto cargará las demás tablas con sus propias PKs

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()